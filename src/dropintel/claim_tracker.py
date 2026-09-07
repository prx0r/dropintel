"""Claim validation tracker — track which claims hold up over time.

Key insight: The most valuable signals are claims that:
1. Get corroborated by multiple independent sources
2. Get validated by actual data/experiments
3. Don't get contradicted

We track these over time and surface the ones that are becoming more可信.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .schemas import SignalOutcome, ValidationStatus, Confidence


# ---------------------------------------------------------------------------
# Claim tracker
# ---------------------------------------------------------------------------

class ClaimTracker:
    """Track claims and their validation status over time."""
    
    def __init__(self):
        self.claims = {}  # claim_hash -> claim data
        self.load_path = Path(__file__).parent.parent.parent / 'data' / 'outcomes' / 'claim_tracker.json'
        self.load()
    
    def load(self):
        """Load existing tracker data."""
        if self.load_path.exists():
            with open(self.load_path) as f:
                data = json.load(f)
                self.claims = data.get('claims', {})
    
    def save(self):
        """Save tracker data."""
        self.load_path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_claims': len(self.claims),
            'claims': self.claims,
        }
        
        with open(self.load_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
    
    def _claim_hash(self, claim_text: str, domain: str) -> str:
        """Generate hash for claim dedup with fuzzy matching."""
        import re
        # Normalize text
        normalized = claim_text.lower().strip()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Extract key terms (numbers, important words)
        key_terms = []
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*[%x]?', normalized)
        if numbers:
            key_terms.extend(numbers[:3])
        # Extract key nouns
        for word in ['revenue', 'conversion', 'traffic', 'ai', 'chatgpt',
                     'shopify', 'mcp', 'agent', 'booking', 'installer',
                     'seo', 'google', 'meta', 'tiktok', 'ads']:
            if word in normalized:
                key_terms.append(word)
        # Build hash from domain + key terms
        key_str = f"{domain}:{'_'.join(sorted(set(key_terms)))}"
        return hashlib.md5(key_str.encode()).hexdigest()[:12]
    
    def add_claim(self, signal: dict):
        """Add or update a claim from a signal."""
        claim_text = signal.get('claim', '')
        domain = signal.get('domain', '')
        handle = signal.get('author_handle', '')
        if isinstance(handle, dict):
            handle = handle.get('userName', '')
        
        claim_hash = self._claim_hash(claim_text, domain)
        
        if claim_hash not in self.claims:
            self.claims[claim_hash] = {
                'claim_id': claim_hash,
                'claim_text': claim_text[:500],
                'domain': domain,
                'first_seen': signal.get('published_at', ''),
                'last_seen': signal.get('published_at', ''),
                'sources': [],
                'source_count': 0,
                'validation_status': 'UNCHECKED',
                'confidence': 'LOW',
                'evidence_strength': 0,
                'has_data': False,
                'quantitative': False,
                'sample_size': None,
            }
        
        claim = self.claims[claim_hash]
        
        # Add source if new
        if handle and handle not in claim['sources']:
            claim['sources'].append(handle)
            claim['source_count'] = len(claim['sources'])
        
        # Update time range
        pub = signal.get('published_at', '')
        if pub and pub < claim['first_seen']:
            claim['first_seen'] = pub
        if pub and pub > claim['last_seen']:
            claim['last_seen'] = pub
        
        # Update evidence
        if signal.get('has_data'):
            claim['has_data'] = True
        if signal.get('claim_quantitative'):
            claim['quantitative'] = True
        if signal.get('sample_size'):
            claim['sample_size'] = signal['sample_size']
        
        # Update validation status
        if claim['source_count'] >= 3:
            claim['validation_status'] = 'SUPPORTED'
            claim['confidence'] = 'HIGH'
        elif claim['source_count'] >= 2:
            claim['validation_status'] = 'SUPPORTED'
            claim['confidence'] = 'MEDIUM'
        
        # Boost confidence for quantitative claims
        if claim['quantitative'] and claim['source_count'] >= 2:
            claim['confidence'] = 'HIGH'
    
    def get_validated_claims(self, min_sources: int = 2) -> list[dict]:
        """Get claims that have been validated by multiple sources."""
        validated = []
        for claim in self.claims.values():
            if claim['source_count'] >= min_sources:
                validated.append(claim)
        
        return sorted(validated, key=lambda x: x['source_count'], reverse=True)
    
    def get_high_confidence_claims(self) -> list[dict]:
        """Get high-confidence claims."""
        return [
            c for c in self.claims.values()
            if c['confidence'] == 'HIGH' or c['source_count'] >= 3
        ]
    
    def get_emerging_claims(self, days: int = 7) -> list[dict]:
        """Get claims from last N days that are gaining traction."""
        cutoff = datetime.now(timezone.utc).isoformat()
        emerging = []
        
        for claim in self.claims.values():
            # Check if recent
            if claim.get('last_seen', '') >= cutoff:
                if claim['source_count'] >= 2:
                    emerging.append(claim)
        
        return sorted(emerging, key=lambda x: x['source_count'], reverse=True)
    
    def generate_report(self) -> dict:
        """Generate validation report."""
        return {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_claims': len(self.claims),
            'validated_claims': len(self.get_validated_claims()),
            'high_confidence': len(self.get_high_confidence_claims()),
            'top_validated': self.get_validated_claims(3)[:10],
            'high_confidence_list': self.get_high_confidence_claims()[:10],
        }


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_claim_tracking():
    """Run claim tracking on all signals."""
    tracker = ClaimTracker()
    
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    all_signals = []
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            all_signals.extend(signals)
    
    print(f"Loaded {len(all_signals)} signals")
    
    # Add claims
    for s in all_signals:
        tracker.add_claim(s)
    
    # Save
    tracker.save()
    
    # Generate report
    report = tracker.generate_report()
    
    print(f"\n=== CLAIM TRACKING REPORT ===")
    print(f"Total claims tracked: {report['total_claims']}")
    print(f"Validated (2+ sources): {report['validated_claims']}")
    print(f"High confidence: {report['high_confidence']}")
    
    print(f"\n=== TOP VALIDATED CLAIMS ===")
    for c in report['top_validated'][:5]:
        print(f"  [{c['source_count']} sources] {c['claim_text'][:80]}...")
        print(f"    Sources: {', '.join(c['sources'])}")
        print(f"    Status: {c['validation_status']} | Confidence: {c['confidence']}")
        print()
    
    return report


if __name__ == "__main__":
    run_claim_tracking()
