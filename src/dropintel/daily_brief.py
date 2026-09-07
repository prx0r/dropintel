"""Daily brief generation — surface high-signal claims and source changes.

Generates a daily intelligence brief from extracted signals.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .schemas import CommerceSignal, DailyBrief


# ---------------------------------------------------------------------------
# Brief generation
# ---------------------------------------------------------------------------

def generate_daily_brief(
    signals: list[dict],
    crossref: Optional[dict] = None,
) -> dict:
    """Generate daily intelligence brief.
    
    Returns dict with:
    - date
    - summary stats
    - top empirical claims
    - top corroborated claims
    - source reputation changes
    - actionable recommendations
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Summary stats
    total = len(signals)
    empirical = [s for s in signals if s.get('signal_type') == 'EMPIRICAL_DATA']
    validations = [s for s in signals if s.get('signal_type') == 'VALIDATION']
    counter = [s for s in signals if s.get('signal_type') == 'COUNTER_EVIDENCE']
    
    # By domain
    domains = {}
    for s in signals:
        d = s.get('domain', 'unknown')
        domains[d] = domains.get(d, 0) + 1
    
    # Top accounts
    accounts = {}
    for s in signals:
        h = s.get('author_handle', 'unknown')
        if isinstance(h, dict):
            h = h.get('userName', 'unknown')
        accounts[h] = accounts.get(h, 0) + 1
    
    # Build brief
    brief = {
        'date': today,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_signals': total,
            'empirical_data': len(empirical),
            'validations': len(validations),
            'counter_evidence': len(counter),
            'unique_accounts': len(accounts),
        },
        'domains': dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)),
        'top_accounts': dict(sorted(accounts.items(), key=lambda x: x[1], reverse=True)[:10]),
        'top_empirical_claims': [],
        'corroborated_claims': [],
        'recommendations': [],
    }
    
    # Top empirical claims (by evidence count)
    for s in sorted(empirical, key=lambda x: x.get('evidence_count', 0), reverse=True)[:10]:
        brief['top_empirical_claims'].append({
            'author': s.get('author_handle', ''),
            'domain': s.get('domain', ''),
            'claim': s.get('claim', '')[:200],
            'quantitative': s.get('claim_quantitative', False),
            'sample_size': s.get('sample_size'),
        })
    
    # Corroborated claims from crossref
    if crossref:
        brief['corroborated_claims'] = crossref.get('corroborated_claims', [])[:5]
        
        # Source reputation
        reputation = crossref.get('source_reputation', {})
        top_sources = sorted(
            reputation.items(),
            key=lambda x: x[1].get('corroboration_rate', 0),
            reverse=True
        )[:5]
        
        brief['top_corroborated_sources'] = [
            {
                'handle': h,
                'corroboration_rate': stats.get('corroboration_rate', 0),
                'total_signals': stats.get('total_signals', 0),
            }
            for h, stats in top_sources
        ]
    
    # Generate recommendations
    brief['recommendations'] = generate_recommendations(brief, crossref)
    
    return brief


def generate_recommendations(brief: dict, crossref: Optional[dict]) -> list[str]:
    """Generate actionable recommendations from the brief."""
    recs = []
    
    # High empirical data count
    if brief['summary']['empirical_data'] > 20:
        recs.append(f"Strong day for empirical data: {brief['summary']['empirical_data']} quantitative claims found")
    
    # Corroborated claims
    if brief.get('corroborated_claims'):
        top = brief['corroborated_claims'][0]
        if top.get('evidence_strength', 0) >= 3:
            recs.append(f"High-confidence corroborated claim: {top.get('claim_text', '')[:80]}...")
    
    # Source reputation
    if brief.get('top_corroborated_sources'):
        top_source = brief['top_corroborated_sources'][0]
        if top_source.get('corroboration_rate', 0) > 0.5:
            recs.append(f"High-corroboration source: @{top_source['handle']} ({top_source['corroboration_rate']:.0%})")
    
    # Domain balance
    domains = brief.get('domains', {})
    if domains.get('AGENTIC_COMMERCE', 0) > 10:
        recs.append("Strong signal flow from agentic commerce domain")
    
    if domains.get('HOME_SERVICES', 0) > 5:
        recs.append("Home services domain showing traction")
    
    return recs


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_brief_markdown(brief: dict) -> str:
    """Format brief as markdown."""
    lines = []
    
    lines.append(f"# DROPINTEL Daily Brief — {brief['date']}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total signals: {brief['summary']['total_signals']}")
    lines.append(f"- Empirical data: {brief['summary']['empirical_data']}")
    lines.append(f"- Validations: {brief['summary']['validations']}")
    lines.append(f"- Counter-evidence: {brief['summary']['counter_evidence']}")
    lines.append(f"- Unique accounts: {brief['summary']['unique_accounts']}")
    lines.append("")
    
    lines.append("## Top Domains")
    for domain, count in list(brief['domains'].items())[:5]:
        lines.append(f"- {domain}: {count}")
    lines.append("")
    
    lines.append("## Top Accounts")
    for handle, count in list(brief['top_accounts'].items())[:5]:
        lines.append(f"- @{handle}: {count} signals")
    lines.append("")
    
    if brief['top_empirical_claims']:
        lines.append("## Top Empirical Claims")
        for claim in brief['top_empirical_claims'][:5]:
            lines.append(f"- @{claim['author']} [{claim['domain']}]: {claim['claim'][:100]}...")
        lines.append("")
    
    if brief.get('corroborated_claims'):
        lines.append("## Corroborated Claims")
        for claim in brief['corroborated_claims'][:3]:
            lines.append(f"- [{claim.get('evidence_strength', 0)} sources] {claim.get('claim_text', '')[:80]}...")
            lines.append(f"  Sources: {', '.join(claim.get('sources', []))}")
        lines.append("")
    
    if brief['recommendations']:
        lines.append("## Recommendations")
        for rec in brief['recommendations']:
            lines.append(f"- {rec}")
        lines.append("")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_daily_brief():
    """Run daily brief generation."""
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    all_signals = []
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            all_signals.extend(signals)
    
    # Load crossref if exists
    crossref_path = Path(__file__).parent.parent.parent / 'data' / 'crossref' / 'claims_crossref.json'
    crossref = None
    if crossref_path.exists():
        with open(crossref_path) as f:
            crossref = json.load(f)
    
    # Generate brief
    brief = generate_daily_brief(all_signals, crossref)
    
    # Save JSON
    output_dir = Path(__file__).parent.parent.parent / 'output' / 'daily_brief'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / f"{brief['date']}.json"
    with open(json_path, 'w') as f:
        json.dump(brief, f, indent=2, default=str)
    
    # Save markdown
    md_path = output_dir / f"{brief['date']}.md"
    md_content = format_brief_markdown(brief)
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    print(f"Daily brief generated:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print()
    print(md_content)
    
    return brief


if __name__ == "__main__":
    run_daily_brief()
