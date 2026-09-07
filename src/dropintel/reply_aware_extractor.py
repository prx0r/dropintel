"""Reply-aware extraction — process raw data with proper context.

This fixes the extraction gap: 935 replies (51% of data) were being ignored.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

from .schemas import CommerceSignal, ThreadPosition
from .extractor import classify_signal, _extract_author_handle


def load_raw_posts(handle: str) -> list[dict]:
    """Load all raw posts for a handle."""
    raw_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
    files = list(raw_dir.glob(f'{handle}_*.json'))
    
    all_posts = []
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
            all_posts.extend(data)
    
    return all_posts


def group_by_conversation(posts: list[dict]) -> dict[str, list[dict]]:
    """Group posts by conversation ID (threads)."""
    conversations = defaultdict(list)
    
    for post in posts:
        conv_id = post.get('conversationId', post.get('id'))
        conversations[conv_id].append(post)
    
    return dict(conversations)


def extract_reply_context(post: dict, all_posts: list[dict]) -> dict:
    """Extract context about what a reply is responding to."""
    if not post.get('isReply') and not post.get('inReplyToId'):
        return {}
    
    reply_to_id = post.get('inReplyToId', '')
    if not reply_to_id:
        return {}
    
    # Find original post
    for p in all_posts:
        if p.get('id') == reply_to_id:
            return {
                'reply_to_id': reply_to_id,
                'reply_to_text': p.get('text', '')[:200],
                'reply_to_author': _extract_author_handle(p),
                'reply_to_likes': p.get('likeCount', 0),
            }
    
    return {'reply_to_id': reply_to_id}


def extract_from_conversation(
    posts: list[dict],
    conversation_id: str,
) -> list[CommerceSignal]:
    """Extract signals from a full conversation/thread."""
    signals = []
    
    # Sort by creation time
    sorted_posts = sorted(posts, key=lambda p: p.get('createdAt', ''))
    
    thread_length = len(sorted_posts)
    
    for i, post in enumerate(sorted_posts):
        # Determine position
        if thread_length == 1:
            position = ThreadPosition.STANDALONE
        elif i == 0:
            position = ThreadPosition.INTRO
        elif i == thread_length - 1:
            position = ThreadPosition.CONCLUSION
        else:
            position = ThreadPosition.BODY
        
        # Get author
        author = post.get('author', {})
        if isinstance(author, dict):
            author_handle = author.get('userName', '')
            author_id = author.get('id', '')
        else:
            author_handle = str(author)
            author_id = ''
        
        # Extract signals
        post_signals = classify_signal(
            text=post.get('text', ''),
            post_id=post.get('id', ''),
            author_handle=author_handle,
            author_id=author_id,
            created_at=post.get('createdAt', ''),
            like_count=post.get('likeCount', 0),
            retweet_count=post.get('retweetCount', 0),
            reply_count=post.get('replyCount', 0),
            quote_count=post.get('quoteCount', 0),
            bookmark_count=post.get('bookmarkCount', 0),
            is_thread=thread_length > 1,
            thread_length=thread_length,
            thread_position=position,
            is_reply=post.get('isReply', False),
            reply_to_id=post.get('inReplyToId'),
        )
        
        signals.extend(post_signals)
    
    return signals


def run_reply_aware_extraction(handle: str) -> dict:
    """Run reply-aware extraction for a single handle."""
    # Load raw posts
    posts = load_raw_posts(handle)
    if not posts:
        return {'handle': handle, 'error': 'No raw posts found'}
    
    # Group by conversation
    conversations = group_by_conversation(posts)
    
    all_signals = []
    threads_found = 0
    replies_found = 0
    
    for conv_id, conv_posts in conversations.items():
        if len(conv_posts) > 1:
            # This is a thread
            threads_found += 1
            signals = extract_from_conversation(conv_posts, conv_id)
            all_signals.extend(signals)
        else:
            # Single post
            post = conv_posts[0]
            if post.get('isReply'):
                replies_found += 1
            
            author = post.get('author', {})
            if isinstance(author, dict):
                author_handle = author.get('userName', '')
                author_id = author.get('id', '')
            else:
                author_handle = str(author)
                author_id = ''
            
            signals = classify_signal(
                text=post.get('text', ''),
                post_id=post.get('id', ''),
                author_handle=author_handle,
                author_id=author_id,
                created_at=post.get('createdAt', ''),
                like_count=post.get('likeCount', 0),
                retweet_count=post.get('retweetCount', 0),
                reply_count=post.get('replyCount', 0),
                quote_count=post.get('quoteCount', 0),
                bookmark_count=post.get('bookmarkCount', 0),
                is_reply=post.get('isReply', False),
                reply_to_id=post.get('inReplyToId'),
            )
            all_signals.extend(signals)
    
    # Dedup
    seen = set()
    unique_signals = []
    for s in all_signals:
        if s.signal_id not in seen:
            seen.add(s.signal_id)
            unique_signals.append(s)
    
    return {
        'handle': handle,
        'total_posts': len(posts),
        'conversations': len(conversations),
        'threads_found': threads_found,
        'replies_found': replies_found,
        'signals_extracted': len(unique_signals),
        'signals': unique_signals,
    }


def run_full_reply_extraction(handles: list[str] = None):
    """Run reply-aware extraction on all accounts."""
    if handles is None:
        # Load all handles from raw data
        raw_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
        handles = list(set(f.stem.split('_')[0] for f in raw_dir.glob('*.json')))
    
    print(f"Running reply-aware extraction on {len(handles)} accounts...")
    
    all_results = {}
    total_signals = 0
    
    for handle in handles:
        print(f"@{handle}...", end=' ', flush=True)
        
        result = run_reply_aware_extraction(handle)
        all_results[handle] = result
        
        if 'error' not in result:
            signals = result['signals']
            
            # Save signals
            from .pipeline import save_signals
            new_s = save_signals(signals, handle)
            
            print(f"{result['total_posts']} posts -> {result['signals_extracted']} signals ({result['threads_found']} threads, {result['replies_found']} replies)")
            total_signals += result['signals_extracted']
        else:
            print(f"ERROR: {result['error']}")
    
    print(f"\nTotal signals: {total_signals}")
    
    # Save results
    output_path = Path(__file__).parent.parent.parent / 'data' / 'extraction_results.json'
    with open(output_path, 'w') as f:
        # Convert signals to dicts for JSON
        serializable = {}
        for handle, result in all_results.items():
            if 'signals' in result:
                serializable[handle] = {
                    'total_posts': result['total_posts'],
                    'conversations': result['conversations'],
                    'threads_found': result['threads_found'],
                    'replies_found': result['replies_found'],
                    'signals_extracted': result['signals_extracted'],
                }
            else:
                serializable[handle] = result
        
        json.dump(serializable, f, indent=2)
    
    return all_results


if __name__ == "__main__":
    run_full_reply_extraction()
