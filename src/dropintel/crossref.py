"""Cross-reference layer — match claims across sources.

When multiple independent sources make the same claim, confidence increases.
When sources contradict each other, we flag it.

Key insight: Aleyda Solís found that 69.6% of AI citations are external.
We need to track which claims are corroborated.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from .schemas import (
    CommerceSignal, ClaimGraph, ValidationStatus, Confidence,
)


# ---------------------------------------------------------------------------
# Claim extraction (simplified NLP)
# ---------------------------------------------------------------------------

# Keywords that indicate quantifiable claims
QUANT_MARKERS = [
    'revenue', 'conversion', 'roas', 'cpa', 'cpc', 'ctr',
    'increase', 'decrease', 'growth', 'scale', 'multiply',
    '%', 'x ', 'times', 'double', 'triple',
    'sessions', 'orders', 'customers', 'sales',
]

# Keywords that indicate tool/platform claims
TOOL_MARKERS = [
    'shopify', 'google ads', 'meta ads', 'tiktok ads',
    'chatgpt', 'gemini', 'perplexity', 'claude',
    'mcp', 'api', 'catalog', 'structured data',
    'hotjar', 'clarity', 'ga4', 'analytics',
]


def extract_claim_key(signal: dict) -> str:
    """Extract a normalized claim key for matching.
    
    This is simplified — in production you'd use embeddings.
    For now, we extract key phrases.
    """
    claim = signal.get('claim', '').lower()
    domain = signal.get('domain', '')
    signal_type = signal.get('signal_type', '')
    
    # Build a simple key from domain + key terms
    key_terms = []
    
    # Extract numbers
    import re
    numbers = re.findall(r'\d+\.?\d*[%x]?', claim)
    if numbers:
        key_terms.extend(numbers[:3])  # First 3 numbers
    
    # Extract key nouns
    for word in ['revenue', 'conversion', 'traffic', 'ai', 'chatgpt', 
                 'shopify', 'mcp', 'agent', 'booking', 'installer']:
        if word in claim:
            key_terms.append(word)
    
    # Build key
    key = f"{domain}:{'_'.join(sorted(set(key_terms)))}"
    return key


def normalize_claim(signal: dict) -> str:
    """Normalize claim text for comparison."""
    claim = signal.get('claim', '').lower().strip()
    
    # Remove punctuation
    import re
    claim = re.sub(r'[^\w\s]', '', claim)
    
    # Remove extra whitespace
    claim = ' '.join(claim.split())
    
    return claim[:200]  # First 200 chars


# ---------------------------------------------------------------------------
# Cross-reference engine
# ---------------------------------------------------------------------------

class CrossReferenceEngine:
    """Match claims across sources and build claim graph."""
    
    def __init__(self):
        self.claims = {}  # claim_key -> ClaimGraph
        self.signals = []  # all signals
    
    def add_signal(self, signal: dict):
        """Add a signal to the cross-reference engine."""
        self.signals.append(signal)
        
        # Extract claim key
        claim_key = extract_claim_key(signal)
        normalized = normalize_claim(signal)
        handle = signal.get('author_handle', '')
        if isinstance(handle, dict):
            handle = handle.get('userName', '')
        
        # Create or update claim
        if claim_key not in self.claims:
            self.claims[claim_key] = ClaimGraph(
                claim_id=claim_key,
                claim_text=normalized,
                first_seen=signal.get('published_at', ''),
            )
        
        claim = self.claims[claim_key]
        
        # Add source if not already present
        if handle not in claim.source_handles:
            claim.source_handles.append(handle)
        
        # Update evidence strength
        claim.evidence_strength = len(claim.source_handles)
        
        # Update validation status
        if claim.evidence_strength >= 3:
            claim.validation_status = ValidationStatus.SUPPORTED
        elif claim.evidence_strength >= 2:
            claim.validation_status = ValidationStatus.SUPPORTED
        
        claim.last_updated = datetime.now(timezone.utc).isoformat()
    
    def find_corroborations(self, min_sources: int = 2) -> list[dict]:
        """Find claims corroborated by multiple sources."""
        corroborated = []
        
        for key, claim in self.claims.items():
            if claim.evidence_strength >= min_sources:
                corroborated.append({
                    'claim_id': claim.claim_id,
                    'claim_text': claim.claim_text,
                    'sources': claim.source_handles,
                    'evidence_strength': claim.evidence_strength,
                    'validation_status': claim.validation_status.value,
                })
        
        return sorted(corroborated, key=lambda x: x['evidence_strength'], reverse=True)
    
    def find_contradictions(self) -> list[dict]:
        """Find claims that contradict each other."""
        # Simplified: look for same domain but different directions
        contradictions = []
        
        # Group by domain
        by_domain = {}
        for signal in self.signals:
            domain = signal.get('domain', '')
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(signal)
        
        # Look for counter-evidence in same domain
        for domain, signals in by_domain.items():
            counter = [s for s in signals if s.get('signal_type') == 'COUNTER_EVIDENCE']
            validation = [s for s in signals if s.get('signal_type') == 'VALIDATION']
            
            if counter and validation:
                contradictions.append({
                    'domain': domain,
                    'counter_signals': len(counter),
                    'validation_signals': len(validation),
                    'counter_examples': [s.get('claim', '')[:100] for s in counter[:2]],
                })
        
        return contradictions
    
    def get_source_reputation(self) -> dict:
        """Calculate source reputation based on corroboration."""
        source_stats = {}
        
        for signal in self.signals:
            handle = signal.get('author_handle', '')
            if isinstance(handle, dict):
                handle = handle.get('userName', '')
            
            if handle not in source_stats:
                source_stats[handle] = {
                    'total_signals': 0,
                    'empirical_signals': 0,
                    'corroborated': 0,
                    'domains': set(),
                }
            
            stats = source_stats[handle]
            stats['total_signals'] += 1
            
            if signal.get('signal_type') == 'EMPIRICAL_DATA':
                stats['empirical_signals'] += 1
            
            stats['domains'].add(signal.get('domain', ''))
            
            # Check if this signal is corroborated
            claim_key = extract_claim_key(signal)
            if claim_key in self.claims:
                claim = self.claims[claim_key]
                if claim.evidence_strength >= 2:
                    stats['corroborated'] += 1
        
        # Convert sets to lists for JSON
        for handle, stats in source_stats.items():
            stats['domains'] = list(stats['domains'])
            stats['corroboration_rate'] = (
                stats['corroborated'] / stats['total_signals'] 
                if stats['total_signals'] > 0 else 0
            )
        
        return source_stats
    
    def save(self, filepath: str):
        """Save cross-reference results."""
        output = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_signals': len(self.signals),
            'total_claims': len(self.claims),
            'corroborated_claims': self.find_corroborations(),
            'contradictions': self.find_contradictions(),
            'source_reputation': self.get_source_reputation(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return output


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_cross_reference():
    """Run cross-reference on all extracted signals."""
    engine = CrossReferenceEngine()
    
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            for s in signals:
                engine.add_signal(s)
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'crossref'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'claims_crossref.json'
    output = engine.save(str(output_path))
    
    print(f"Cross-reference complete:")
    print(f"  Signals: {output['total_signals']}")
    print(f"  Unique claims: {output['total_claims']}")
    print(f"  Corroborated: {len(output['corroborated_claims'])}")
    print(f"  Contradictions: {len(output['contradictions'])}")
    
    # Show top corroborated claims
    print("\n=== TOP CORROBORATED CLAIMS ===")
    for claim in output['corroborated_claims'][:10]:
        print(f"  [{claim['evidence_strength']} sources] {claim['claim_text'][:80]}...")
        print(f"    Sources: {', '.join(claim['sources'])}")
        print()
    
    # Show source reputation
    print("=== TOP SOURCES BY CORROBORATION RATE ===")
    sorted_sources = sorted(
        output['source_reputation'].items(),
        key=lambda x: x[1]['corroboration_rate'],
        reverse=True
    )
    for handle, stats in sorted_sources[:10]:
        if stats['total_signals'] >= 3:
            print(f"  @{handle}: {stats['corroboration_rate']:.0%} corroborated ({stats['total_signals']} signals)")
    
    return output


if __name__ == "__main__":
    run_cross_reference()
