"""Commerce signal extractor — evidence-grounded classification.

Extracts CommerceSignal from X posts with exact evidence spans.
Adapted from BEAR's extractor_v2.py for commerce intelligence.

Key differences from BEAR:
1. Domain-specific keyword sets (AEO, Google Ads, Meta, CRO, etc.)
2. Quantitative claim detection (numbers, sample sizes)
3. Tool/platform recommendations
4. Thread and reply awareness
5. Self-reported vs independent verification

Source fidelity outranks what the model thinks is true.
"""

import re
import hashlib
from datetime import datetime, timezone
from typing import Optional

from .schemas import (
    CommerceSignal, EvidenceSpan, SignalType, Domain, Confidence,
    ThreadPosition, RawPost,
)


# ---------------------------------------------------------------------------
# Classification constants
# ---------------------------------------------------------------------------

# Signal type keywords
EMPIRICAL_KW = [
    'study', 'data', 'research', 'analysis', 'measured', 'tested',
    'experiment', 'results', 'found that', 'showed', 'verified',
    'according to', 'survey', 'sample', 'n=', 'sessions',
    'conversion rate', 'revenue', 'roas', 'cpa', 'cpc',
    'click-through', 'impressions', 'grew by', 'increased by',
    'decreased by', 'x higher', 'x more', '% higher', '% more',
]

TACTICAL_KW = [
    'you should', 'do this', 'stop doing', 'start doing',
    'best practice', 'pro tip', 'hack', 'strategy',
    'how to', 'step by step', 'guide', 'tutorial',
    'switch from', 'move to', 'replace with', 'instead of',
    'the key is', 'focus on', 'prioritize',
]

TOOL_KW = [
    'use this tool', 'try this', 'recommend', 'switch to',
    'migrated to', 'now using', 'replaced with',
    'shopify', 'google ads', 'meta ads', 'tiktok ads',
    'analytics', 'gsc', 'search console', 'ga4',
    'hotjar', 'clarity', 'postscript', 'klaviyo',
    'fermàt', 'catalog api', 'checkout blocks',
]

CASE_STUDY_KW = [
    'case study', 'client results', 'our results', 'we achieved',
    'before and after', 'shipped', 'launched', 'grew from',
    'generated', 'scaled to', 'hit', 'reached',
    'from $', 'to $', 'from x', 'to x',
]

# Domain keywords
DOMAIN_PATTERNS = {
    Domain.AEO: [
        r'\baoe\b', r'\bai engine optimization\b', r'\bchatgpt\b',
        r'\bgemini\b', r'\bperplexity\b', r'\bclaude\b',
        r'\bentourage\b', r'\bai search\b', r'\bllm\b',
        r'\bstructured data\b', r'\bschema\b', r'\brich snippet\b',
        r'\bmention\b', r'\bcitation\b', r'\breference\b',
        r'\bproduct feed\b', r'\bcatalog api\b',
    ],
    Domain.GOOGLE_ADS: [
        r'\bgoogle ads\b', r'\bpmax\b', r'\bperformance max\b',
        r'\bshopping\b', r'\bmerchant center\b', r'\bcpc\b',
        r'\broas\b', r'\bcpa\b', r'\bsearch ads\b',
        r'\bdisplay ads\b', r'\byoutube ads\b', r'\bgleads\b',
    ],
    Domain.META_CREATIVE: [
        r'\bmeta ads\b', r'\bfacebook ads\b', r'\big ads\b',
        r'\btiktok ads\b', r'\bcreative\b', r'\bad creative\b',
        r'\bhook\b', r'\bthumbnail\b', r'\bvideo ad\b',
        r'\bcbo\b', r'\bad set\b', r'\bcampaign budget\b',
    ],
    Domain.CRO: [
        r'\bcro\b', r'\bconversion rate\b', r'\blanding page\b',
        r'\bcheckout\b', r'\badd to cart\b', r'\babandon\b',
        r'\ba\/b test\b', r'\bsplit test\b', r'\buser testing\b',
        r'\bheatmaps?\b', r'\bscroll depth\b', r'\bclarity\b',
    ],
    Domain.PRODUCT_DISCOVERY: [
        r'\bproduct discovery\b', r'\bproduct find\b',
        r'\bsocial commerce\b', r'\bproduct feed\b',
        r'\bshopping feed\b', r'\bmerchant center\b',
        r'\bproduct title\b', r'\bproduct description\b',
    ],
    Domain.INTERNATIONAL: [
        r'\blocalization\b', r'\blocali[sz]e\b', r'\btranslation\b',
        r'\bcross.border\b', r'\binternational\b', r'\bmulti.country\b',
        r'\bnordic\b', r'\bscandinavian\b', r'\beuropean\b',
        r'\bnorwegian\b', r'\bswedish\b', r'\bgerman\b',
        r'\bnon.english\b',
    ],
    Domain.AGENTIC_COMMERCE: [
        r'\bagentic\b', r'\bagent\b', r'\bai agent\b',
        r'\btool calling\b', r'\bfunction calling\b',
        r'\bapi\b', r'\bstructured\b', r'\bmachine readable\b',
        r'\bllm\b', r'\bretrieval\b', r'\brag\b',
    ],
    Domain.DTC_ECONOMICS: [
        r'\bdtc\b', r'\bunit economics\b', r'\bcontribution margin\b',
        r'\bacos\b', r'\bltv\b', r'\bcac\b', r'\baov\b',
        r'\bmargin\b', r'\bprofit\b', r'\bp&l\b', r'\beconomics\b',
    ],
    Domain.AMAZON: [
        r'\bamazon\b', r'\bfba\b', r'\bppc\b', r'\bsponsored\b',
        r'\bbrand analytics\b', r'\bsearch analytics\b',
    ],
    Domain.DROPSHIPPING: [
        r'\bdropshipping\b', r'\bdropship\b', r'\baliexpress\b',
        r'\bsupplier\b', r'\bfulfillment\b', r'\bshipping time\b',
    ],
    Domain.PERFORMANCE_MARKETING: [
        r'\bmedia buying\b', r'\bscal(e|ing)\b', r'\bbudget\b',
        r'\bspend\b', r'\bacquisition\b', r'\bprospect(ing|ion)\b',
        r'\bretarget\b', r'\bremarketing\b',
    ],
    Domain.SHOPIFY: [
        r'\bshopify\b', r'\bcheckout\b', r'\btheme\b',
        r'\bapp\b', r'\bplugin\b', r'\bliquid\b',
    ],
}

# Quantitative patterns
NUMBER_PATTERNS = [
    (r'(\d{1,3}[,.]?\d{3,})\s*(sessions?|visits?|orders?|revenue|sales?)', 'absolute'),
    (r'\$[\d,.]+[kmb]?', 'dollar'),
    (r'(\d+\.?\d*)\s*[xX×]', 'multiplier'),
    (r'(\d+\.?\d*)%', 'percentage'),
    (r'n\s*=\s*(\d+)', 'sample_size'),
    (r'(\d+)\s*(stores?|brands?|merchants?|shops?)', 'sample_count'),
]

# Negation / retrospective / promotional
NEGATION = ['not', "n't", 'never', 'no ', 'stop', 'avoid', "don't"]
RETRO_KW = ['was', 'were', 'told you', 'called it', 'said so', 'yesterday', 'last year']
PROMO_KW = ['course', 'launch', 'subscribe', 'join', 'sign up', 'dm me', 'link in bio',
            'free guide', 'download', 'webinar', 'workshop']


# ---------------------------------------------------------------------------
# Evidence span finder
# ---------------------------------------------------------------------------

def find_quote_span(text: str, keyword: str) -> tuple[int, int]:
    """Find exact char positions of keyword in text."""
    idx = text.lower().find(keyword.lower())
    if idx >= 0:
        return idx, idx + len(keyword)
    return -1, -1


def find_regex_span(text: str, pattern: str) -> tuple[int, int]:
    """Find exact char positions via regex."""
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return m.start(), m.end()
    return -1, -1


# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------

def detect_domains(text: str) -> list[tuple[Domain, EvidenceSpan]]:
    """Detect which domains a post touches."""
    lower = text.lower()
    domains = []
    
    for domain, patterns in DOMAIN_PATTERNS.items():
        for pat in patterns:
            m = re.search(pat, lower)
            if m:
                domains.append((domain, EvidenceSpan(
                    field="domain",
                    post_id="",
                    quote=text[m.start():m.end()],
                    start_char=m.start(),
                    end_char=m.end(),
                )))
                break  # One match per domain
    
    return domains


# ---------------------------------------------------------------------------
# Quantitative detection
# ---------------------------------------------------------------------------

def detect_quantitative(text: str) -> tuple[bool, Optional[str], list[EvidenceSpan]]:
    """Detect if post has quantitative claims. Returns (is_quant, sample_size, evidence)."""
    lower = text.lower()
    evidence = []
    sample_size = None
    
    for pat, kind in NUMBER_PATTERNS:
        m = re.search(pat, lower)
        if m:
            evidence.append(EvidenceSpan(
                field="quantitative",
                post_id="",
                quote=text[m.start():m.end()],
                start_char=m.start(),
                end_char=m.end(),
            ))
            if kind == 'sample_size':
                sample_size = m.group(1)
            elif kind == 'sample_count':
                sample_size = m.group(0)
    
    return len(evidence) > 0, sample_size, evidence


# ---------------------------------------------------------------------------
# Main classifier
# ---------------------------------------------------------------------------

def classify_signal(
    text: str,
    post_id: str,
    author_handle: str,
    author_id: str = "",
    created_at: str = "",
    like_count: int = 0,
    retweet_count: int = 0,
    reply_count: int = 0,
    quote_count: int = 0,
    bookmark_count: int = 0,
    is_thread: bool = False,
    thread_length: int = 1,
    thread_position: ThreadPosition = ThreadPosition.STANDALONE,
    is_reply: bool = False,
    reply_to_id: Optional[str] = None,
    reply_to_author: Optional[str] = None,
) -> list[CommerceSignal]:
    """Classify a post into one or more CommerceSignals with evidence.
    
    Key principle: evidence spans are REQUIRED for all non-null fields.
    """
    lower = text.lower()
    signals = []
    
    # --- Filter: promotional ---
    if any(w in lower for w in PROMO_KW):
        return []  # Skip promotional content entirely
    
    # --- Filter: too short ---
    if len(text.strip()) < 30:
        return []
    
    # --- Detect domains ---
    domains = detect_domains(text)
    if not domains:
        return []  # No commerce relevance detected
    
    # --- Detect quantitative ---
    is_quant, sample_size, quant_evidence = detect_quantitative(text)
    
    # --- Detect methodology ---
    methodology = None
    if any(w in lower for w in ['shopify analytics', 'ga4', 'google analytics', 'hotjar', 'clarity']):
        methodology = "analytics_platform"
    elif any(w in lower for w in ['study', 'research', 'survey', 'analysis']):
        methodology = "formal_study"
    elif any(w in lower for w in ['we tested', 'we ran', 'experiment', 'a/b test']):
        methodology = "internal_test"
    elif any(w in lower for w in ['i noticed', 'observed', 'saw that', 'looks like']):
        methodology = "observation"
    
    # --- Detect signal type ---
    signal_type = SignalType.OBSERVATION  # default
    
    if any(w in lower for w in EMPIRICAL_KW) and is_quant:
        signal_type = SignalType.EMPIRICAL_DATA
    elif any(w in lower for w in CASE_STUDY_KW):
        signal_type = SignalType.CASE_STUDY
    elif any(w in lower for w in TOOL_KW):
        signal_type = SignalType.TOOL_RECOMMENDATION
    elif any(w in lower for w in TACTICAL_KW):
        signal_type = SignalType.TACTICAL_CLAIM
    elif any(w in lower for w in ['disagree', 'actually', 'wrong', 'not true', 'pushback']):
        signal_type = SignalType.COUNTER_EVIDENCE
    elif any(w in lower for w in ['confirm', 'agree', 'exactly', 'this', 'can verify']):
        signal_type = SignalType.VALIDATION
    
    # --- Detect recommendation direction ---
    recommendation = None
    if any(w in lower for w in ['you should', 'do this', 'start', 'switch to', 'use this']):
        recommendation = "DO_THIS"
    elif any(w in lower for w in ['stop', 'avoid', 'don\'t', 'never', 'instead of']):
        recommendation = "AVOID_THIS"
    
    # --- Detect data linkage ---
    has_data = bool(re.search(r'https?://|\.com|\.io|dashboard|report|study', lower))
    has_code = bool(re.search(r'github\.com|npm |pip |api|documentation', lower))
    
    # --- Build claim (first 200 chars) ---
    claim = text[:200].replace('\n', ' ').strip()
    if len(text) > 200:
        claim += "..."
    
    # --- Create signals (one per domain) ---
    for domain, domain_evidence in domains:
        signal_id = f"sig_{post_id}_{domain.value}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        # Evidence spans
        evidence = [domain_evidence]
        evidence.extend(quant_evidence)
        
        # Conviction
        conviction = Confidence.MEDIUM
        if is_quant and sample_size:
            conviction = Confidence.HIGH
        elif is_quant:
            conviction = Confidence.MEDIUM
        elif has_data:
            conviction = Confidence.MEDIUM
        else:
            conviction = Confidence.LOW
        
        signal = CommerceSignal(
            signal_id=signal_id,
            post_id=post_id,
            author_handle=author_handle,
            author_id=author_id,
            published_at=created_at or datetime.now(timezone.utc).isoformat(),
            signal_type=signal_type,
            domain=domain,
            claim=claim,
            claim_quantitative=is_quant,
            sample_size=sample_size,
            methodology=methodology,
            recommendation=recommendation,
            is_self_reported=not has_data,
            has_data=has_data,
            has_code=has_code,
            is_thread=is_thread,
            thread_length=thread_length,
            thread_position=thread_position,
            is_reply=is_reply,
            reply_to_id=reply_to_id,
            reply_to_author=reply_to_author,
            like_count=like_count,
            retweet_count=retweet_count,
            reply_count=reply_count,
            quote_count=quote_count,
            bookmark_count=bookmark_count,
            conviction=conviction,
            evidence=evidence,
            extracted_at=datetime.now(timezone.utc).isoformat(),
        )
        signals.append(signal)
    
    return signals


def _extract_author_handle(post: dict) -> str:
    """Extract author handle from post, handling nested author objects."""
    # Try direct handle first
    handle = post.get('author_handle', '')
    if handle and isinstance(handle, str):
        return handle
    
    # Try nested author object
    author = post.get('author', '')
    if isinstance(author, dict):
        return author.get('userName', author.get('screen_name', ''))
    elif isinstance(author, str):
        return author
    
    # Try other fields
    return post.get('username', post.get('user', {}).get('screen_name', ''))


def extract_all(posts: list[dict]) -> list[CommerceSignal]:
    """Extract signals from all posts. Input: list of post dicts."""
    all_signals = []
    for post in posts:
        handle = _extract_author_handle(post)
        signals = classify_signal(
            text=post.get('text', ''),
            post_id=post.get('tweet_id', post.get('id', '')),
            author_handle=handle,
            author_id=post.get('author_id', post.get('author', {}).get('id', '') if isinstance(post.get('author'), dict) else ''),
            created_at=post.get('created_at', ''),
            like_count=post.get('likes', post.get('like_count', 0)),
            retweet_count=post.get('retweets', post.get('retweet_count', 0)),
            reply_count=post.get('replies', post.get('reply_count', 0)),
            quote_count=post.get('quote_count', post.get('quote_count', 0)),
            bookmark_count=post.get('bookmark_count', 0),
        )
        all_signals.extend(signals)
    return all_signals
