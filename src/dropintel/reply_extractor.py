"""Reply-aware signal extractor.

Replies in ecommerce X contain the ACTUAL operator reasoning.
When someone asks "why did you switch from Meta to Google?" and the operator
explains their reasoning — that's gold.

Key insight from BEAR: replies are underused. We make them primary.
"""

from typing import Optional

from .schemas import (
    CommerceSignal, EvidenceSpan, SignalType, Domain, Confidence,
    ThreadPosition, RawPost,
)
from .extractor import classify_signal, detect_domains


def extract_from_replies(
    replies: list[dict],
    original_post: dict,
    original_author: str = "",
) -> list[CommerceSignal]:
    """Extract signals from replies to a post.
    
    Reply types:
    - CLARIFICATION: Original author adds detail
    - VALIDATION: Someone confirms the claim
    - COUNTER_EVIDENCE: Someone disagrees
    - SUBSTANTIVE: Long, detailed reply with new info
    
    The highest signal replies are:
    1. Original author clarifying (CLARIFICATION)
    2. Other operators sharing similar experience (VALIDATION)
    3. Detailed counter-arguments with data (COUNTER_EVIDENCE)
    
    Args:
        replies: List of reply post dicts
        original_post: The post being replied to
        original_author: Handle of original author
    
    Returns:
        List of CommerceSignals with reply context
    """
    if not replies:
        return []
    
    all_signals = []
    original_text = original_post.get('text', '')
    
    for reply in replies:
        reply_text = reply.get('text', '')
        reply_author = reply.get('author_handle', reply.get('author', ''))
        
        # Skip low-effort replies (< 50 chars)
        if len(reply_text.strip()) < 50:
            continue
        
        # Skip pure link drops
        if reply_text.startswith('http') and len(reply_text) < 100:
            continue
        
        # Determine reply type
        reply_type = _classify_reply_type(reply_text, reply_author, original_author)
        
        # Extract signals
        signals = classify_signal(
            text=reply_text,
            post_id=reply.get('tweet_id', reply.get('id', '')),
            author_handle=reply_author,
            author_id=reply.get('author_id', ''),
            created_at=reply.get('created_at', ''),
            like_count=reply.get('likes', reply.get('like_count', 0)),
            retweet_count=reply.get('retweets', reply.get('retweet_count', 0)),
            reply_count=reply.get('replies', reply.get('reply_count', 0)),
            quote_count=reply.get('quote_count', 0),
            bookmark_count=reply.get('bookmark_count', 0),
            is_reply=True,
            reply_to_id=original_post.get('tweet_id', original_post.get('id', '')),
            reply_to_author=original_author,
        )
        
        # Enrich with reply type
        for signal in signals:
            signal.signal_type = reply_type
            
            # Add reply context evidence
            signal.evidence.append(EvidenceSpan(
                field="reply_context",
                post_id=reply.get('tweet_id', reply.get('id', '')),
                quote=f"Reply to @{original_author}: {reply_type.value}",
                start_char=0,
                end_char=0,
            ))
            
            # Boost conviction for original author replies
            if reply_author == original_author:
                signal.conviction = Confidence.HIGH
                signal.evidence.append(EvidenceSpan(
                    field="author_clarification",
                    post_id=reply.get('tweet_id', reply.get('id', '')),
                    quote="Original author clarifying their own claim",
                    start_char=0,
                    end_char=0,
                ))
            
            # Boost for data-containing replies
            if any(w in reply_text.lower() for w in ['%', 'x ', '$', 'revenue', 'data']):
                signal.has_data = True
                if signal.conviction == Confidence.LOW:
                    signal.conviction = Confidence.MEDIUM
        
        all_signals.extend(signals)
    
    return all_signals


def _classify_reply_type(
    reply_text: str,
    reply_author: str,
    original_author: str,
) -> SignalType:
    """Classify the type of reply."""
    lower = reply_text.lower()
    
    # Original author clarifying
    if reply_author == original_author:
        if any(w in lower for w in ['clarify', 'to add', 'also', 'edit:', 'update:', 'correction']):
            return SignalType.CLARIFICATION
        return SignalType.CLARIFICATION  # Author replying to own post = clarification
    
    # Validation
    if any(w in lower for w in ['confirm', 'agree', 'exactly', 'this', 'can verify',
                                  'same experience', 'we saw', 'our results']):
        return SignalType.VALIDATION
    
    # Counter-evidence
    if any(w in lower for w in ['disagree', 'actually', 'wrong', 'not true', 'pushback',
                                  'however', 'but', 'contrary', 'opposite']):
        return SignalType.COUNTER_EVIDENCE
    
    # Default to clarification (substantive reply)
    return SignalType.CLARIFICATION


def score_reply_quality(reply: dict, original: dict) -> dict:
    """Score reply quality for prioritization.
    
    Returns dict with:
    - quality_score: 0-100
    - is_author_reply: bool
    - has_data: bool
    - has_experience: bool
    - depth: str (SHALLOW, MEDIUM, DEEP)
    """
    text = reply.get('text', '')
    reply_author = reply.get('author_handle', reply.get('author', ''))
    original_author = original.get('author_handle', original.get('author', ''))
    
    score = 0
    lower = text.lower()
    
    # Length (proxy for depth)
    if len(text) > 100:
        score += 20
    if len(text) > 300:
        score += 20
    if len(text) > 500:
        score += 10
    
    # Author reply bonus (highest signal)
    if reply_author == original_author:
        score += 30
    
    # Data indicators
    has_data = any(w in lower for w in ['%', 'x ', '$', 'revenue', 'data', 'saw', 'measured'])
    if has_data:
        score += 20
    
    # Experience indicators
    has_experience = any(w in lower for w in ['we', 'our', 'i', 'my', 'tested', 'tried', 'switched'])
    if has_experience:
        score += 15
    
    # Engagement
    likes = reply.get('likes', reply.get('like_count', 0))
    if likes > 10:
        score += 10
    
    # Depth classification
    if len(text) > 300:
        depth = "DEEP"
    elif len(text) > 100:
        depth = "MEDIUM"
    else:
        depth = "SHALLOW"
    
    return {
        "quality_score": min(score, 100),
        "is_author_reply": reply_author == original_author,
        "has_data": has_data,
        "has_experience": has_experience,
        "depth": depth,
    }


def prioritize_replies(replies: list[dict], original: dict) -> list[dict]:
    """Prioritize replies by quality for extraction.
    
    Returns replies sorted by quality score (highest first).
    """
    scored = []
    for reply in replies:
        quality = score_reply_quality(reply, original)
        scored.append((quality["quality_score"], reply))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [reply for _, reply in scored]


def should_fetch_replies(post: dict) -> bool:
    """Decide if a post is worth fetching replies for.
    
    Fetch replies for:
    - Posts with high engagement (replies > 5)
    - Posts from high-tier accounts
    - Posts that are questions (invite discussion)
    - Posts with controversial claims
    """
    text = post.get('text', '').lower()
    reply_count = post.get('replies', post.get('reply_count', 0))
    
    # High engagement
    if reply_count > 5:
        return True
    
    # Questions invite discussion
    if '?' in text:
        return True
    
    # Controversial claims
    if any(w in text for w in ['actually', 'unpopular opinion', 'hot take', 'controversial']):
        return True
    
    # Data posts invite validation
    if any(w in text for w in ['%', 'x ', '$', 'study', 'data', 'results']):
        return True
    
    return False
