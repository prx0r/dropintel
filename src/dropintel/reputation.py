"""Source reputation scoring — track who's actually right.

Key insight from BEAR: source reputation is the most valuable long-term asset.
We track accuracy rate, empirical rate, and corroboration rate per source.

Sources that consistently make claims that get corroborated get higher scores.
Sources that make claims that get contradicted get lower scores.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .schemas import SourceReputation, Confidence


# ---------------------------------------------------------------------------
# Reputation calculator
# ---------------------------------------------------------------------------

class ReputationEngine:
    """Calculate source reputation from signals and crossref data."""
    
    def __init__(self):
        self.sources = {}  # handle -> stats
        self.crossref = None
    
    def load_signals(self, signals: list[dict]):
        """Load all signals and calculate stats."""
        for s in signals:
            handle = s.get('author_handle', '')
            if isinstance(handle, dict):
                handle = handle.get('userName', '')
            
            if not handle:
                continue
            
            if handle not in self.sources:
                self.sources[handle] = {
                    'handle': handle,
                    'total_signals': 0,
                    'empirical_signals': 0,
                    'case_studies': 0,
                    'validations': 0,
                    'counter_evidence': 0,
                    'tool_recommendations': 0,
                    'high_conviction': 0,
                    'has_data': 0,
                    'is_thread': 0,
                    'domains': {},
                    'first_seen': s.get('published_at', ''),
                    'last_seen': s.get('published_at', ''),
                }
            
            stats = self.sources[handle]
            stats['total_signals'] += 1
            
            # Track time range
            pub = s.get('published_at', '')
            if pub and pub < stats['first_seen']:
                stats['first_seen'] = pub
            if pub and pub > stats['last_seen']:
                stats['last_seen'] = pub
            
            # Signal type stats
            sig_type = s.get('signal_type', '')
            if sig_type == 'EMPIRICAL_DATA':
                stats['empirical_signals'] += 1
            elif sig_type == 'CASE_STUDY':
                stats['case_studies'] += 1
            elif sig_type == 'VALIDATION':
                stats['validations'] += 1
            elif sig_type == 'COUNTER_EVIDENCE':
                stats['counter_evidence'] += 1
            elif sig_type == 'TOOL_RECOMMENDATION':
                stats['tool_recommendations'] += 1
            
            # Conviction
            if s.get('conviction') == 'HIGH':
                stats['high_conviction'] += 1
            
            # Data linkage
            if s.get('has_data'):
                stats['has_data'] += 1
            
            # Thread participation
            if s.get('is_thread'):
                stats['is_thread'] += 1
            
            # Domain tracking
            domain = s.get('domain', '')
            if domain:
                stats['domains'][domain] = stats['domains'].get(domain, 0) + 1
    
    def load_crossref(self, crossref: dict):
        """Load crossref data for corroboration scoring."""
        self.crossref = crossref
    
    def calculate_scores(self) -> dict:
        """Calculate reputation scores for all sources."""
        if not self.crossref:
            return self.sources
        
        # Get corroboration data
        source_reputation = self.crossref.get('source_reputation', {})
        
        for handle, stats in self.sources.items():
            # Base empirical rate
            if stats['total_signals'] > 0:
                stats['empirical_rate'] = stats['empirical_signals'] / stats['total_signals']
            else:
                stats['empirical_rate'] = 0
            
            # Corroboration rate from crossref
            if handle in source_reputation:
                crossref_stats = source_reputation[handle]
                stats['corroboration_rate'] = crossref_stats.get('corroboration_rate', 0)
                stats['corroborated_count'] = crossref_stats.get('corroborated', 0)
            else:
                stats['corroboration_rate'] = 0
                stats['corroborated_count'] = 0
            
            # Quality score (weighted)
            stats['quality_score'] = (
                stats['empirical_rate'] * 30 +
                stats['corroboration_rate'] * 40 +
                (stats['high_conviction'] / max(stats['total_signals'], 1)) * 20 +
                (stats['has_data'] / max(stats['total_signals'], 1)) * 10
            )
            
            # Tier
            if stats['quality_score'] > 60:
                stats['tier'] = 'GOLD'
            elif stats['quality_score'] > 40:
                stats['tier'] = 'SILVER'
            elif stats['quality_score'] > 20:
                stats['tier'] = 'BRONZE'
            else:
                stats['tier'] = 'UNRANKED'
            
            # Confidence
            if stats['total_signals'] >= 10 and stats['empirical_signals'] >= 5:
                stats['confidence'] = 'HIGH'
            elif stats['total_signals'] >= 5:
                stats['confidence'] = 'MEDIUM'
            else:
                stats['confidence'] = "LOW"
        
        return self.sources
    
    def save(self, filepath: str):
        """Save reputation scores."""
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_sources': len(self.sources),
            'sources': self.sources,
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return output
    
    def get_top_sources(self, n: int = 10) -> list[dict]:
        """Get top N sources by quality score."""
        sorted_sources = sorted(
            self.sources.values(),
            key=lambda x: x.get('quality_score', 0),
            reverse=True
        )
        return sorted_sources[:n]


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_reputation_scoring():
    """Run reputation scoring on all signals."""
    engine = ReputationEngine()
    
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    all_signals = []
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            all_signals.extend(signals)
    
    print(f"Loaded {len(all_signals)} signals")
    
    engine.load_signals(all_signals)
    
    # Load crossref if exists
    crossref_path = Path(__file__).parent.parent.parent / 'data' / 'crossref' / 'claims_crossref.json'
    if crossref_path.exists():
        with open(crossref_path) as f:
            crossref = json.load(f)
        engine.load_crossref(crossref)
    
    # Calculate scores
    engine.calculate_scores()
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'scores'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'source_reputation.json'
    output = engine.save(str(output_path))
    
    # Print top sources
    print(f"\n=== TOP 10 SOURCES BY QUALITY SCORE ===")
    for s in engine.get_top_sources(10):
        print(f"@{s['handle']}: {s['quality_score']:.1f} ({s['tier']})")
        print(f"  Signals: {s['total_signals']} | Empirical: {s['empirical_signals']} | Corroborated: {s.get('corroborated_count', 0)}")
        print(f"  Empirical rate: {s['empirical_rate']:.0%} | Corroboration rate: {s['corroboration_rate']:.0%}")
        print(f"  Domains: {', '.join(list(s['domains'].keys())[:3])}")
        print()
    
    return output


if __name__ == "__main__":
    run_reputation_scoring()
