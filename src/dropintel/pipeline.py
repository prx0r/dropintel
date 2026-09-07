"""Pipeline — fetch, extract, score, store.

Modeled after BEAR's pipeline.py but adapted for commerce intelligence.

Flow:
1. FETCH — GetXAPI calls (budget-tracked)
2. STORE RAW — Never throw away paid data
3. EXTRACT — classify_signal + thread/reply awareness
4. CROSS-REF — Match claims across sources
5. SCORE — Source reputation
6. OUTPUT — Daily brief, source cards, claim graph
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from .schemas import (
    RawPost, CommerceSignal, SignalOutcome, SourceReputation,
    Domain, Confidence, ValidationStatus,
)
from .extractor import classify_signal, extract_all
from .thread_extractor import extract_from_thread, score_thread_quality
from .reply_extractor import extract_from_replies, should_fetch_replies


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
SCORES_DIR = DATA_DIR / "scores"
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

GETXAPI_KEY = os.environ.get("GETXAPI_KEY", "")
GETXAPI_BASE = "https://api.getxapi.com/twitter"
COST_PER_TWEET = 0.00005  # $0.05 / 1k


# ---------------------------------------------------------------------------
# GetXAPI Client
# ---------------------------------------------------------------------------

class GetXClient:
    """GetXAPI client with budget tracking."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or GETXAPI_KEY
        self.client = httpx.Client(
            base_url=GETXAPI_BASE,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=15.0,
        )
        self.total_cost = 0.0
        self.total_calls = 0
    
    def _track(self, n_tweets: int, cost: float = None):
        if cost is None:
            cost = n_tweets * COST_PER_TWEET
        self.total_cost += cost
        self.total_calls += 1
        return cost
    
    def get_user_info(self, username: str) -> dict:
        """Get user info with permanent userId."""
        resp = self.client.get("/user/info", params={"userName": username})
        resp.raise_for_status()
        self._track(0)
        return resp.json()
    
    def user_posts(self, username: str, limit: int = 20, cursor: str = "") -> dict:
        """Get user timeline WITH replies and thread expansion."""
        params = {"userName": username, "count": min(limit, 40)}
        if cursor:
            params["cursor"] = cursor
        
        # Use /user/tweets/complete for tweets + replies + thread expansion
        resp = self.client.get("/user/tweets/complete", params=params)
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("tweets", data.get("data", []))
        self._track(len(tweets), cost=0.003)  # $0.003 for complete endpoint
        return data
    
    def user_posts_basic(self, username: str, limit: int = 20, cursor: str = "") -> dict:
        """Get user timeline (tweets only, no replies). Cheaper."""
        params = {
            "q": f"from:{username}",
            "product": "Latest",
            "count": min(limit, 20),
        }
        if cursor:
            params["cursor"] = cursor
        
        resp = self.client.get("/tweet/advanced_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("tweets", data.get("data", []))
        self._track(len(tweets))
        return data
    
    def get_thread(self, tweet_id: str) -> dict:
        """Get full thread."""
        resp = self.client.get("/tweet/thread", params={"id": tweet_id})
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("tweets", data.get("data", []))
        self._track(len(tweets))
        return data
    
    def get_replies(self, tweet_id: str, limit: int = 20) -> dict:
        """Get replies to a specific tweet."""
        params = {"id": tweet_id}
        resp = self.client.get("/tweet/replies", params=params)
        resp.raise_for_status()
        data = resp.json()
        replies = data.get("replies", [])
        self._track(len(replies))
        return data
    
    def search(self, query: str, limit: int = 20, since: str = "", until: str = "") -> dict:
        """Advanced search."""
        params = {
            "q": query,
            "product": "Latest",
            "count": min(limit, 20),
        }
        if since:
            params["since_time"] = since
        if until:
            params["until_time"] = until
        
        resp = self.client.get("/tweet/advanced_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("tweets", data.get("data", []))
        self._track(len(tweets))
        return data
    
    def close(self):
        self.client.close()


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def save_raw(posts: list[dict], handle: str, source: str = "timeline"):
    """Save raw posts. Never throw away paid data."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"{handle}_{source}_{date_str}.json"
    filepath = RAW_DIR / filename
    
    # Append if exists
    existing = []
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)
    
    # Dedup by tweet_id
    existing_ids = {p.get('tweet_id', p.get('id')) for p in existing}
    new_posts = [p for p in posts if p.get('tweet_id', p.get('id')) not in existing_ids]
    
    all_posts = existing + new_posts
    with open(filepath, 'w') as f:
        json.dump(all_posts, f, indent=2, default=str)
    
    return len(new_posts)


def save_signals(signals: list[CommerceSignal], handle: str):
    """Save extracted signals."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"{handle}_signals_{date_str}.json"
    filepath = EXTRACTED_DIR / filename
    
    # Convert to dicts
    signal_dicts = []
    for s in signals:
        d = {
            "signal_id": s.signal_id,
            "post_id": s.post_id,
            "author_handle": s.author_handle,
            "published_at": s.published_at,
            "signal_type": s.signal_type.value,
            "domain": s.domain.value,
            "claim": s.claim,
            "claim_quantitative": s.claim_quantitative,
            "sample_size": s.sample_size,
            "methodology": s.methodology,
            "recommendation": s.recommendation,
            "is_self_reported": s.is_self_reported,
            "has_data": s.has_data,
            "is_thread": s.is_thread,
            "thread_length": s.thread_length,
            "thread_position": s.thread_position.value,
            "is_reply": s.is_reply,
            "conviction": s.conviction.value,
            "evidence_count": len(s.evidence),
            "extracted_at": s.extracted_at,
        }
        signal_dicts.append(d)
    
    # Append if exists
    existing = []
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)
    
    existing_ids = {s['signal_id'] for s in existing}
    new_signals = [s for s in signal_dicts if s['signal_id'] not in existing_ids]
    
    all_signals = existing + new_signals
    with open(filepath, 'w') as f:
        json.dump(all_signals, f, indent=2)
    
    return len(new_signals)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def fetch_account(
    client: GetXClient,
    handle: str,
    max_pages: int = 3,
) -> list[dict]:
    """Fetch recent posts from an account.
    
    Returns raw posts (not filtered).
    """
    all_posts = []
    cursor = ""
    
    for page in range(max_pages):
        data = client.user_posts(handle, limit=20, cursor=cursor)
        tweets = data.get("tweets", data.get("data", []))
        all_posts.extend(tweets)
        
        if not data.get("has_next_page", data.get("has_more", False)):
            break
        
        cursor = data.get("next_cursor", data.get("cursor", ""))
        if not cursor:
            break
        
        time.sleep(0.3)  # Rate limit respect
    
    return all_posts


def fetch_with_threads(
    client: GetXClient,
    handle: str,
    max_posts: int = 20,
) -> tuple[list[dict], list[list[dict]]]:
    """Fetch posts and detect threads.
    
    Returns:
        - all_posts: flat list of all posts
        - threads: list of threads (each thread is a list of posts)
    """
    # Get timeline
    data = client.user_posts(handle, limit=max_posts)
    posts = data.get("tweets", data.get("data", []))
    
    all_posts = list(posts)
    threads = []
    
    # Detect threads (posts that are part of a thread)
    for post in posts:
        # Check if this is a thread starter
        if post.get('conversation_id') == post.get('id') or post.get('tweet_id') == post.get('conversation_id'):
            # Fetch full thread
            try:
                thread_data = client.get_thread(post.get('id', post.get('tweet_id', '')))
                thread_posts = thread_data.get("tweets", thread_data.get("data", []))
                if len(thread_posts) > 1:
                    threads.append(thread_posts)
                    # Add thread posts to all_posts (dedup later)
                    existing_ids = {p.get('id', p.get('tweet_id')) for p in all_posts}
                    for tp in thread_posts:
                        tp_id = tp.get('id', tp.get('tweet_id'))
                        if tp_id not in existing_ids:
                            all_posts.append(tp)
                            existing_ids.add(tp_id)
            except Exception:
                pass  # Skip failed thread fetches
    
    return all_posts, threads


def extract_signals(
    posts: list[dict],
    threads: list[list[dict]],
    handle: str,
) -> list[CommerceSignal]:
    """Extract signals from posts and threads."""
    all_signals = []
    
    # Extract from standalone posts
    for post in posts:
        # Skip if part of a thread (will be extracted as thread)
        is_thread_part = False
        for thread in threads:
            thread_ids = {p.get('id', p.get('tweet_id')) for p in thread}
            if post.get('id', post.get('tweet_id')) in thread_ids:
                is_thread_part = True
                break
        
        if not is_thread_part:
            # Handle nested author object
            author = post.get('author', {})
            if isinstance(author, dict):
                author_handle = post.get('author_handle', author.get('userName', handle))
                author_id = post.get('author_id', author.get('id', ''))
            else:
                author_handle = post.get('author_handle', str(author) if author else handle)
                author_id = post.get('author_id', '')
            
            signals = classify_signal(
                text=post.get('text', ''),
                post_id=post.get('id', post.get('tweet_id', '')),
                author_handle=author_handle,
                author_id=author_id,
                created_at=post.get('created_at', ''),
                like_count=post.get('likes', post.get('like_count', 0)),
                retweet_count=post.get('retweets', post.get('retweet_count', 0)),
                reply_count=post.get('replies', post.get('reply_count', 0)),
                quote_count=post.get('quote_count', 0),
                bookmark_count=post.get('bookmark_count', 0),
            )
            all_signals.extend(signals)
    
    # Extract from threads (higher priority)
    for thread in threads:
        thread_signals = extract_from_thread(thread)
        all_signals.extend(thread_signals)
    
    # Dedup by signal_id
    seen = set()
    unique_signals = []
    for s in all_signals:
        if s.signal_id not in seen:
            seen.add(s.signal_id)
            unique_signals.append(s)
    
    return unique_signals


def run_pipeline(
    handles: list[str],
    client: GetXClient = None,
    max_posts_per_account: int = 20,
) -> dict:
    """Run full pipeline for a list of handles.
    
    Returns summary dict with stats.
    """
    if client is None:
        client = GetXClient()
    
    results = {
        "handles_processed": 0,
        "total_posts_fetched": 0,
        "total_threads_found": 0,
        "total_signals_extracted": 0,
        "total_cost_usd": 0.0,
        "handles": {},
    }
    
    for handle in handles:
        print(f"\n{'='*60}")
        print(f"Processing: @{handle}")
        print(f"{'='*60}")
        
        try:
            # Fetch
            posts, threads = fetch_with_threads(client, handle, max_posts_per_account)
            print(f"  Fetched {len(posts)} posts, {len(threads)} threads")
            
            # Store raw
            new_posts = save_raw(posts, handle, "timeline")
            print(f"  Stored {new_posts} new raw posts")
            
            # Extract
            signals = extract_signals(posts, threads, handle)
            new_signals = save_signals(signals, handle)
            print(f"  Extracted {len(signals)} signals ({new_signals} new)")
            
            # Track
            results["handles_processed"] += 1
            results["total_posts_fetched"] += len(posts)
            results["total_threads_found"] += len(threads)
            results["total_signals_extracted"] += len(signals)
            results["handles"][handle] = {
                "posts": len(posts),
                "threads": len(threads),
                "signals": len(signals),
            }
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results["handles"][handle] = {"error": str(e)}
        
        time.sleep(0.5)  # Between accounts
    
    results["total_cost_usd"] = client.total_cost
    client.close()
    
    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"  Handles processed: {results['handles_processed']}")
    print(f"  Posts fetched: {results['total_posts_fetched']}")
    print(f"  Threads found: {results['total_threads_found']}")
    print(f"  Signals extracted: {results['total_signals_extracted']}")
    print(f"  Total cost: ${results['total_cost_usd']:.4f}")
    
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    
    # Load accounts
    accounts_file = CONFIG_DIR / "accounts.json"
    if accounts_file.exists():
        with open(accounts_file) as f:
            config = json.load(f)
        handles = [a["handle"] for a in config.get("accounts", [])]
    else:
        handles = sys.argv[1:] or ["kurtinc"]
    
    print(f"Running pipeline for {len(handles)} accounts...")
    results = run_pipeline(handles)
    
    # Save results
    output_file = DATA_DIR / "pipeline_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
