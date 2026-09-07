"""Canonical data types for DROPINTEL commerce signal intelligence.

Modeled after BEAR's schemas but adapted for:
- Commerce signals (not crypto trades)
- Claims with validation (not price outcomes)
- Thread/reply-aware extraction
- Multi-domain reputation (AEO, Google Ads, Meta, CRO, etc.)

Source fidelity outranks what the model thinks is true.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SignalType(str, Enum):
    EMPIRICAL_DATA = "EMPIRICAL_DATA"       # Has numbers, sample size, methodology
    TACTICAL_CLAIM = "TACTICAL_CLAIM"       # "Do X to get Y"
    STRATEGIC_VIEW = "STRATEGIC_VIEW"       # Opinion on direction
    TOOL_RECOMMENDATION = "TOOL_RECOMMENDATION"  # Use this tool/platform
    CASE_STUDY = "CASE_STUDY"              # Full case study with outcomes
    OBSERVATION = "OBSERVATION"             # Noticed something
    COUNTER_EVIDENCE = "COUNTER_EVIDENCE"   # Contradicts another claim
    VALIDATION = "VALIDATION"               # Confirms another claim
    CLARIFICATION = "CLARIFICATION"         # Adds detail to own claim


class Domain(str, Enum):
    AEO = "AEO"                           # AI Engine Optimization
    GOOGLE_ADS = "GOOGLE_ADS"             # Google Ads, PMax, Shopping
    META_CREATIVE = "META_CREATIVE"       # Meta/TikTok creative, ad creative
    CRO = "CRO"                           # Conversion rate optimization
    PRODUCT_DISCOVERY = "PRODUCT_DISCOVERY"  # How products get found
    INTERNATIONAL = "INTERNATIONAL"       # Cross-border, localization
    AGENTIC_COMMERCE = "AGENTIC_COMMERCE"  # AI agents, agentic checkout
    DTC_ECONOMICS = "DTC_ECONOMICS"       # Unit economics, P&L, margins
    SHOPIFY = "SHOPIFY"                   # Shopify-specific
    AMAZON = "AMAZON"                     # Amazon marketplace
    DROPSHIPPING = "DROPSHIPPING"         # Dropshipping ops
    PERFORMANCE_MARKETING = "PERFORMANCE_MARKETING"  # Media buying, ROAS
    SEO = "SEO"                           # Organic search
    CONTENT = "CONTENT"                   # Content marketing


class Confidence(str, Enum):
    HIGH = "HIGH"           # Multiple independent confirmations
    MEDIUM = "MEDIUM"       # Single source with data
    LOW = "LOW"             # Single source, no data
    DISPUTED = "DISPUTED"   # Conflicting evidence


class ValidationStatus(str, Enum):
    UNCHECKED = "UNCHECKED"
    SUPPORTED = "SUPPORTED"         # Others confirmed
    CONTRADICTED = "CONTRADICTED"   # Others disagree
    INCONCLUSIVE = "INCONCLUSIVE"   # Not enough data
    OUTDATED = "OUTDATED"           # No longer relevant


class ThreadPosition(str, Enum):
    STANDALONE = "STANDALONE"       # Not a thread
    INTRO = "INTRO"                 # First post in thread
    BODY = "BODY"                   # Middle of thread
    CONCLUSION = "CONCLUSION"       # Last post in thread


# ---------------------------------------------------------------------------
# Core Data Classes
# ---------------------------------------------------------------------------

@dataclass
class EvidenceSpan:
    """Exact quote supporting a field value. Required for every non-null field."""
    field: str
    post_id: str
    quote: str
    start_char: int
    end_char: int
    provenance: str = "EXPLICIT"  # EXPLICIT, INFERRED, CONTEXT_RESOLVED


@dataclass
class RawPost:
    """Immutable X post. This is the source of truth. Never filtered during ingestion."""
    tweet_id: str
    author_id: str
    author_handle: str
    created_at: str            # ISO 8601 UTC
    created_at_ms: int
    text: str
    conversation_id: str
    reply_to_id: Optional[str] = None
    quote_id: Optional[str] = None
    repost_of_id: Optional[str] = None
    media_ids: list[str] = field(default_factory=list)
    raw_sha256: str = ""
    provider: str = ""         # getxapi
    ingestion_version: str = "1.0"
    observed_at: str = ""      # when we fetched it


@dataclass
class CommerceSignal:
    """Extracted commerce signal from a post.
    
    One post can yield multiple signals.
    Every non-null field MUST have an evidence span.
    """
    signal_id: str
    post_id: str
    author_handle: str
    author_id: str
    published_at: str          # ISO 8601 UTC

    # Classification
    signal_type: SignalType
    domain: Domain
    
    # Content
    claim: str                              # The actual claim text
    claim_quantitative: bool = False        # Has numbers?
    sample_size: Optional[str] = None       # "94M sessions", "10 stores"
    methodology: Optional[str] = None       # "shopify_analytics", "internal_test"
    
    # Direction (for tactical claims)
    recommendation: Optional[str] = None    # "DO_THIS" or "AVOID_THIS"
    
    # Source credibility signals
    is_self_reported: bool = True           # "I did X" vs independent
    has_data: bool = False                  # Links to dashboards/studies
    has_code: bool = False                  # Links to repo/tool
    
    # Thread context
    is_thread: bool = False
    thread_length: int = 1
    thread_position: ThreadPosition = ThreadPosition.STANDALONE
    
    # Reply context
    is_reply: bool = False
    reply_to_id: Optional[str] = None
    reply_to_author: Optional[str] = None
    
    # Engagement quality (snapshots, not features)
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    bookmark_count: int = 0
    
    # Conviction
    conviction: Confidence = Confidence.MEDIUM
    
    # Evidence — REQUIRED for all non-null fields
    evidence: list[EvidenceSpan] = field(default_factory=list)
    
    # Provenance
    extraction_version: str = "1.0"
    extracted_at: str = ""


@dataclass
class SignalOutcome:
    """Did the claim hold up over time?
    
    One signal can have multiple validation events.
    """
    signal_id: str
    
    # Validation
    validation_status: ValidationStatus = ValidationStatus.UNCHECKED
    confidence_at_extraction: Confidence = Confidence.MEDIUM
    confidence_now: Confidence = Confidence.MEDIUM
    
    # Replication
    replicated_by: list[str] = field(default_factory=list)      # handles
    contradicted_by: list[str] = field(default_factory=list)    # handles
    
    # Time
    claim_age_days: int = 0
    still_relevant: bool = True
    
    # Cross-reference
    related_signal_ids: list[str] = field(default_factory=list)
    
    # Outcome notes
    validation_notes: str = ""
    
    # Provenance
    outcome_version: str = "1.0"
    last_checked_at: str = ""


@dataclass
class SourceReputation:
    """Source × domain × direction × timeframe.
    
    This is the canonical reputation unit. Never collapse dimensions.
    """
    handle: str
    source_id: str
    domain: str
    
    # Stats
    n: int = 0
    n_quantitative: int = 0      # Claims with data
    n_validated: int = 0         # Claims confirmed
    n_contradicted: int = 0      # Claims disproven
    
    # Scores
    accuracy_rate: float = 0.0   # validated / (validated + contradicted)
    empirical_rate: float = 0.0  # quantitative claims / total
    mean_engagement: float = 0.0
    
    # Bayesian prior
    bayesian_accuracy: float = 0.5
    confidence: str = "insufficient"  # sufficient, limited, insufficient
    
    # Metadata
    first_seen: str = ""
    last_seen: str = ""
    tier: str = "BRONZE"         # GOLD, SILVER, BRONZE


@dataclass
class ClaimGraph:
    """Relationships between claims across sources."""
    claim_id: str
    claim_text: str
    source_handles: list[str] = field(default_factory=list)
    
    # Relationships
    confirms: list[str] = field(default_factory=list)     # claim_ids this confirms
    contradicts: list[str] = field(default_factory=list)  # claim_ids this contradicts
    extends: list[str] = field(default_factory=list)      # claim_ids this builds on
    
    # Status
    validation_status: ValidationStatus = ValidationStatus.UNCHECKED
    evidence_strength: int = 0  # number of independent sources
    
    # Metadata
    first_seen: str = ""
    last_updated: str = ""


@dataclass
class DailyBrief:
    """Daily intelligence summary."""
    date: str                    # YYYY-MM-DD
    
    # New signals
    new_signals: list[CommerceSignal] = field(default_factory=list)
    new_validations: list[SignalOutcome] = field(default_factory=list)
    
    # Source changes
    reputation_changes: list[dict] = field(default_factory=list)
    
    # Top claims
    emerging_claims: list[ClaimGraph] = field(default_factory=list)
    
    # Actionable
    recommended_actions: list[str] = field(default_factory=list)
    
    # Stats
    total_posts_fetched: int = 0
    total_signals_extracted: int = 0
    total_cost_usd: float = 0.0
