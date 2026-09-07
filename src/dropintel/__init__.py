"""DROPINTEL — Commerce signal intelligence from X/Twitter.

Modeled after BEAR's signal extraction but adapted for:
- Commerce signals (not crypto trades)
- Claims with validation (not price outcomes)
- Thread/reply-aware extraction
- Multi-domain reputation (AEO, Google Ads, Meta, CRO, etc.)
"""

from .schemas import (
    CommerceSignal, SignalOutcome, SourceReputation, ClaimGraph,
    RawPost, EvidenceSpan, DailyBrief,
    SignalType, Domain, Confidence, ValidationStatus, ThreadPosition,
)
from .extractor import classify_signal, extract_all
from .thread_extractor import extract_from_thread, score_thread_quality
from .reply_extractor import extract_from_replies, should_fetch_replies
from .pipeline import GetXClient, run_pipeline

__version__ = "1.0.0"
