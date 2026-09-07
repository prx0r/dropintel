"""Thread-aware signal extractor.

Threads are the full case study in ecommerce X.
The INTRO is the hook, the BODY has the evidence, the CONCLUSION has the CTA.

Key insight from BEAR: threads are underused. We make them primary.
"""

from typing import Optional

from .schemas import (
    CommerceSignal, EvidenceSpan, SignalType, Domain, Confidence,
    ThreadPosition, RawPost,
)
from .extractor import classify_signal, detect_domains


def extract_from_thread(
    thread_posts: list[dict],
    thread_id: str = "",
) -> list[CommerceSignal]:
    """Extract signals from a full thread.
    
    Thread structure:
    - First post = INTRO (hook, headline claim)
    - Middle posts = BODY (evidence, reasoning, data)
    - Last post = CONCLUSION (summary, CTA)
    
    The BODY posts are typically highest signal because they contain
    the actual evidence and reasoning.
    
    Args:
        thread_posts: List of post dicts, ordered from first to last
        thread_id: The root tweet ID (optional)
    
    Returns:
        List of CommerceSignals with thread context
    """
    if not thread_posts:
        return []
    
    all_signals = []
    thread_length = len(thread_posts)
    root_id = thread_id or thread_posts[0].get('tweet_id', thread_posts[0].get('id', ''))
    
    for i, post in enumerate(thread_posts):
        # Determine thread position
        if thread_length == 1:
            position = ThreadPosition.STANDALONE
        elif i == 0:
            position = ThreadPosition.INTRO
        elif i == thread_length - 1:
            position = ThreadPosition.CONCLUSION
        else:
            position = ThreadPosition.BODY
        
        # Handle nested author object
        author = post.get('author', {})
        if isinstance(author, dict):
            author_handle = post.get('author_handle', author.get('userName', ''))
            author_id = post.get('author_id', author.get('id', ''))
        else:
            author_handle = post.get('author_handle', str(author) if author else '')
            author_id = post.get('author_id', '')
        
        # Extract signals from this post
        signals = classify_signal(
            text=post.get('text', ''),
            post_id=post.get('tweet_id', post.get('id', '')),
            author_handle=author_handle,
            author_id=author_id,
            created_at=post.get('created_at', ''),
            like_count=post.get('likes', post.get('like_count', 0)),
            retweet_count=post.get('retweets', post.get('retweet_count', 0)),
            reply_count=post.get('replies', post.get('reply_count', 0)),
            quote_count=post.get('quote_count', 0),
            bookmark_count=post.get('bookmark_count', 0),
            is_thread=True,
            thread_length=thread_length,
            thread_position=position,
        )
        
        # Boost conviction for body posts (they have the evidence)
        for signal in signals:
            signal.evidence.append(EvidenceSpan(
                field="thread_context",
                post_id=post.get('tweet_id', post.get('id', '')),
                quote=f"Thread position: {position.value} of {thread_length}",
                start_char=0,
                end_char=0,
            ))
            
            # Body posts get conviction boost
            if position == ThreadPosition.BODY:
                if signal.conviction == Confidence.LOW:
                    signal.conviction = Confidence.MEDIUM
                elif signal.conviction == Confidence.MEDIUM:
                    signal.conviction = Confidence.HIGH
            
            # Threads with 4+ posts get overall boost
            if thread_length >= 4:
                signal.evidence.append(EvidenceSpan(
                    field="thread_depth",
                    post_id=post.get('tweet_id', post.get('id', '')),
                    quote=f"Deep thread ({thread_length} posts) — indicates thorough explanation",
                    start_char=0,
                    end_char=0,
                ))
        
        all_signals.extend(signals)
    
    return all_signals


def score_thread_quality(thread_posts: list[dict]) -> dict:
    """Score thread quality for prioritization.
    
    Returns dict with:
    - quality_score: 0-100
    - has_data: bool
    - has_visuals: bool
    - reply_engagement: int
    - reasoning_depth: str (SHALLOW, MEDIUM, DEEP)
    """
    if not thread_posts:
        return {"quality_score": 0}
    
    score = 0
    has_data = False
    has_visuals = False
    total_replies = 0
    text_lengths = []
    
    for post in thread_posts:
        text = post.get('text', '')
        text_lengths.append(len(text))
        
        # Data indicators
        if any(w in text.lower() for w in ['%', 'x ', '$', 'revenue', 'sessions', 'conversion', 'data']):
            has_data = True
            score += 15
        
        # Visual indicators
        if post.get('media_ids') or post.get('media'):
            has_visuals = True
            score += 10
        
        # Engagement
        total_replies += post.get('replies', post.get('reply_count', 0))
        
        # Text length (longer = more detailed)
        if len(text) > 200:
            score += 10
        if len(text) > 500:
            score += 10
    
    # Thread length bonus
    thread_length = len(thread_posts)
    if thread_length >= 5:
        score += 20
    elif thread_length >= 3:
        score += 10
    
    # Reasoning depth from text lengths
    avg_len = sum(text_lengths) / len(text_lengths) if text_lengths else 0
    if avg_len > 300:
        reasoning_depth = "DEEP"
        score += 15
    elif avg_len > 150:
        reasoning_depth = "MEDIUM"
        score += 10
    else:
        reasoning_depth = "SHALLOW"
    
    # Reply engagement bonus
    if total_replies > 20:
        score += 15
    elif total_replies > 5:
        score += 10
    
    return {
        "quality_score": min(score, 100),
        "has_data": has_data,
        "has_visuals": has_visuals,
        "reply_engagement": total_replies,
        "reasoning_depth": reasoning_depth,
        "thread_length": thread_length,
    }


def prioritize_threads(threads: list[list[dict]]) -> list[list[dict]]:
    """Prioritize threads by quality for extraction.
    
    Returns threads sorted by quality score (highest first).
    """
    scored = []
    for thread in threads:
        quality = score_thread_quality(thread)
        scored.append((quality["quality_score"], thread))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [thread for _, thread in scored]
