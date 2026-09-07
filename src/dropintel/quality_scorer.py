"""Signal quality scorer — distinguish alpha from noise.

Key insight: Not all signals are equal. We need to score:
1. Thread depth (long threads = more thought)
2. Reply engagement (replies = discussion = alpha)
3. Empirical content (numbers, data, studies)
4. Corroboration (multiple sources = stronger)
5. Source reputation (who's saying it)

The best signals are:
- Quantitative claims from high-reputation sources
- Corroborated by multiple independent sources
- In deep threads with lots of discussion
- From accounts with high empirical rates
"""

import json
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Quality scoring
# ---------------------------------------------------------------------------

def score_signal_quality(
    signal: dict,
    source_reputation: dict = None,
    crossref: dict = None,
) -> dict:
    """Score a signal for quality.
    
    Returns dict with:
    - quality_score: 0-100
    - quality_tier: GOLD/SILVER/BRONZE/NOISE
    - reasons: list of quality indicators
    """
    score = 0
    reasons = []
    
    # 1. Empirical content (0-30 points)
    if signal.get('signal_type') == 'EMPIRICAL_DATA':
        score += 20
        reasons.append("Empirical data claim")
        
        if signal.get('claim_quantitative'):
            score += 10
            reasons.append("Quantitative claim")
        
        if signal.get('sample_size'):
            score += 5
            reasons.append(f"Sample size: {signal['sample_size']}")
    
    elif signal.get('signal_type') == 'CASE_STUDY':
        score += 15
        reasons.append("Case study")
    
    elif signal.get('signal_type') == 'VALIDATION':
        score += 10
        reasons.append("Validation of another claim")
    
    # 2. Thread context (0-20 points)
    if signal.get('is_thread'):
        thread_len = signal.get('thread_length', 1)
        if thread_len >= 5:
            score += 20
            reasons.append(f"Deep thread ({thread_len} posts)")
        elif thread_len >= 3:
            score += 15
            reasons.append(f"Medium thread ({thread_len} posts)")
        else:
            score += 10
            reasons.append(f"Short thread ({thread_len} posts)")
    
    # 3. Engagement quality (0-15 points)
    # Use engagement as snapshot, not feature
    likes = signal.get('like_count', 0)
    replies = signal.get('reply_count', 0)
    quotes = signal.get('quote_count', 0)
    
    if replies > 10:
        score += 15
        reasons.append(f"High reply engagement ({replies})")
    elif replies > 5:
        score += 10
        reasons.append(f"Medium reply engagement ({replies})")
    
    if quotes > 5:
        score += 5
        reasons.append(f"Quote tweet engagement ({quotes})")
    
    # 4. Source reputation (0-15 points)
    handle = signal.get('author_handle', '')
    if isinstance(handle, dict):
        handle = handle.get('userName', '')
    
    if source_reputation and handle in source_reputation:
        rep = source_reputation[handle]
        empirical_rate = rep.get('empirical_rate', 0)
        corroboration_rate = rep.get('corroboration_rate', 0)
        
        if empirical_rate > 0.3:
            score += 10
            reasons.append(f"High empirical source ({empirical_rate:.0%})")
        
        if corroboration_rate > 0.3:
            score += 5
            reasons.append(f"High corroboration source ({corroboration_rate:.0%})")
    
    # 5. Corroboration (0-20 points)
    if crossref:
        claim_text = signal.get('claim', '')[:200]
        for claim in crossref.get('corroborated_claims', []):
            if claim.get('evidence_strength', 0) >= 3:
                # Check if this signal is about the same claim
                if any(h == handle for h in claim.get('sources', [])):
                    score += 20
                    reasons.append(f"Corroborated by {claim['evidence_strength']} sources")
                    break
            elif claim.get('evidence_strength', 0) >= 2:
                if any(h == handle for h in claim.get('sources', [])):
                    score += 10
                    reasons.append(f"Corroborated by {claim['evidence_strength']} sources")
                    break
    
    # 6. Data linkage (0-5 points)
    if signal.get('has_data'):
        score += 5
        reasons.append("Links to data/dashboard")
    
    # 7. Conviction (0-5 points)
    if signal.get('conviction') == 'HIGH':
        score += 5
        reasons.append("High conviction extraction")
    
    # Cap at 100
    score = min(score, 100)
    
    # Determine tier
    if score >= 70:
        tier = 'GOLD'
    elif score >= 50:
        tier = 'SILVER'
    elif score >= 30:
        tier = 'BRONZE'
    else:
        tier = 'NOISE'
    
    return {
        'quality_score': score,
        'quality_tier': tier,
        'reasons': reasons,
    }


def score_all_signals(
    signals: list[dict],
    source_reputation: dict = None,
    crossref: dict = None,
) -> list[dict]:
    """Score all signals and return sorted by quality."""
    scored = []
    
    for s in signals:
        quality = score_signal_quality(s, source_reputation, crossref)
        s['quality_score'] = quality['quality_score']
        s['quality_tier'] = quality['quality_tier']
        s['quality_reasons'] = quality['reasons']
        scored.append(s)
    
    # Sort by quality score
    scored.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    return scored


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_quality_scoring():
    """Run quality scoring on all signals."""
    # Load reputation
    reputation_path = Path(__file__).parent.parent.parent / 'data' / 'scores' / 'source_reputation.json'
    source_reputation = None
    if reputation_path.exists():
        with open(reputation_path) as f:
            data = json.load(f)
            source_reputation = data.get('sources', {})
    
    # Load crossref
    crossref_path = Path(__file__).parent.parent.parent / 'data' / 'crossref' / 'claims_crossref.json'
    crossref = None
    if crossref_path.exists():
        with open(crossref_path) as f:
            crossref = json.load(f)
    
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    all_signals = []
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            all_signals.extend(signals)
    
    print(f"Loaded {len(all_signals)} signals")
    
    # Score
    scored = score_all_signals(all_signals, source_reputation, crossref)
    
    # Count by tier
    tiers = {}
    for s in scored:
        tier = s.get('quality_tier', 'NOISE')
        tiers[tier] = tiers.get(tier, 0) + 1
    
    print(f"\n=== QUALITY DISTRIBUTION ===")
    for tier in ['GOLD', 'SILVER', 'BRONZE', 'NOISE']:
        print(f"  {tier}: {tiers.get(tier, 0)}")
    
    # Show top signals
    print(f"\n=== TOP 10 HIGHEST QUALITY SIGNALS ===")
    for s in scored[:10]:
        handle = s.get('author_handle', '')
        if isinstance(handle, dict):
            handle = handle.get('userName', '')
        print(f"  [{s['quality_tier']}] {s['quality_score']} pts | @{handle}")
        print(f"    {s.get('claim', '')[:100]}...")
        print(f"    Reasons: {', '.join(s.get('quality_reasons', [])[:3])}")
        print()
    
    # Save scored signals
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'scores'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'scored_signals.json'
    with open(output_path, 'w') as f:
        json.dump(scored[:100], f, indent=2, default=str)  # Top 100
    
    print(f"Saved top 100 scored signals to {output_path}")
    
    return scored


if __name__ == "__main__":
    run_quality_scoring()
