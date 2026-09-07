"""Smart two-pass pipeline — tweets first, threads + replies second.

Strategy:
1. PASS 1: /user/tweets ($0.001) — get all tweets, identify threads
2. PASS 2: /user/tweets/complete ($0.003) — only for accounts with threads

This saves money and focuses expensive calls where threads exist.
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
    Domain, Confidence, ValidationStatus, ThreadPosition,
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
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

GETXAPI_KEY = os.environ.get("GETXAPI_KEY", "")
GETXAPI_BASE = "https://api.getxapi.com/twitter"


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
    
    def _track(self, cost: float):
        self.total_cost += cost
        self.total_calls += 1
    
    def get_user_info(self, username: str) -> dict:
        """Get user info."""
        resp = self.client.get("/user/info", params={"userName": username})
        resp.raise_for_status()
        self._track(0.001)
        return resp.json()
    
    def user_posts(self, username: str, limit: int = 20, cursor: str = "") -> dict:
        """PASS 1: Get user timeline (tweets only). $0.001."""
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
        self._track(0.001)
        return data
    
    def user_posts_complete(self, username: str, limit: int = 40, cursor: str = "") -> dict:
        """PASS 2: Get tweets + replies + thread expansion. $0.003."""
        params = {"userName": username, "count": min(limit, 40)}
        if cursor:
            params["cursor"] = cursor
        
        resp = self.client.get("/user/tweets/complete", params=params)
        resp.raise_for_status()
        data = resp.json()
        self._track(0.003)
        return data
    
    def get_thread(self, tweet_id: str) -> dict:
        """Get full thread. $0.005."""
        resp = self.client.get("/tweet/thread", params={"id": tweet_id})
        resp.raise_for_status()
        data = resp.json()
        self._track(0.005)
        return data
    
    def get_replies(self, tweet_id: str) -> dict:
        """Get replies to a tweet. $0.001."""
        params = {"id": tweet_id}
        resp = self.client.get("/tweet/replies", params=params)
        resp.raise_for_status()
        data = resp.json()
        replies = data.get("replies", [])
        self._track(0.001)
        return data
    
    def search(self, query: str, limit: int = 20) -> dict:
        """Advanced search. $0.001."""
        params = {
            "q": query,
            "product": "Latest",
            "count": min(limit, 20),
        }
        resp = self.client.get("/tweet/advanced_search", params=params)
        resp.raise_for_status()
        data = resp.json()
        self._track(0.001)
        return data
    
    def close(self):
        self.client.close()


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def save_raw(posts: list[dict], handle: str, source: str = "timeline"):
    """Save raw posts."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"{handle}_{source}_{date_str}.json"
    filepath = RAW_DIR / filename
    
    existing = []
    if filepath.exists():
        with open(filepath) as f:
            existing = json.load(f)
    
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
# Two-pass pipeline
# ---------------------------------------------------------------------------

def is_thread_starter(post: dict) -> bool:
    """Check if a post is likely a thread starter."""
    text = post.get('text', '')
    
    # Thread indicators
    thread_markers = [
        'thread:', '🧵', 'a/', '1/',
        'let me explain', 'here is what', 'big thread',
        'long post', 'deep dive', 'breakdown',
    ]
    
    for marker in thread_markers:
        if marker.lower() in text.lower():
            return True
    
    # Check if post has reply indicator (continuation)
    if post.get('in_reply_to_status_id'):
        return False
    
    # Check if text is long (likely thread)
    if len(text) > 200:
        return True
    
    return False


def extract_handle_from_post(post: dict) -> str:
    """Extract author handle from post."""
    author = post.get('author', {})
    if isinstance(author, dict):
        return post.get('author_handle', author.get('userName', ''))
    return post.get('author_handle', str(author) if author else '')


def run_smart_pipeline(
    handles: list[str],
    client: GetXClient = None,
    max_posts_per_account: int = 20,
) -> dict:
    """Run smart two-pass pipeline.
    
    PASS 1: Get tweets, identify threads
    PASS 2: Get complete (threads + replies) for thread-heavy accounts
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
    
    print("=" * 60)
    print("PASS 1: Fetching tweets to identify threads")
    print("=" * 60)
    
    accounts_with_threads = []
    
    for handle in handles:
        print(f"\n@{handle}...", end=' ', flush=True)
        
        try:
            # PASS 1: Get tweets (cheap)
            data = client.user_posts(handle, limit=max_posts_per_account)
            posts = data.get("tweets", data.get("data", []))
            
            # Identify threads
            thread_starters = [p for p in posts if is_thread_starter(p)]
            standalone = [p for p in posts if not is_thread_starter(p)]
            
            print(f"{len(posts)} tweets, {len(thread_starters)} potential threads")
            
            # Save raw
            new = save_raw(posts, handle, "pass1")
            
            # Extract signals from standalone posts
            all_signals = []
            for post in standalone:
                signals = classify_signal(
                    text=post.get('text', ''),
                    post_id=post.get('id', post.get('tweet_id', '')),
                    author_handle=extract_handle_from_post(post),
                    author_id=post.get('author_id', ''),
                    created_at=post.get('created_at', ''),
                    like_count=post.get('likes', post.get('like_count', 0)),
                    retweet_count=post.get('retweets', post.get('retweet_count', 0)),
                    reply_count=post.get('replies', post.get('reply_count', 0)),
                    quote_count=post.get('quote_count', 0),
                    bookmark_count=post.get('bookmark_count', 0),
                )
                all_signals.extend(signals)
            
            new_s = save_signals(all_signals, handle)
            
            results["handles"][handle] = {
                "pass1_posts": len(posts),
                "pass1_signals": len(all_signals),
                "thread_starters": len(thread_starters),
            }
            
            # Track accounts with threads for pass 2
            if thread_starters:
                accounts_with_threads.append({
                    "handle": handle,
                    "thread_starters": thread_starters,
                    "posts": posts,
                })
            
            results["total_posts_fetched"] += len(posts)
            results["total_signals_extracted"] += len(all_signals)
            
        except Exception as e:
            print(f"ERROR: {e}")
            results["handles"][handle] = {"error": str(e)}
        
        time.sleep(0.3)
    
    print(f"\n{'=' * 60}")
    print(f"PASS 2: Fetching complete for {len(accounts_with_threads)} accounts with threads")
    print("=" * 60)
    
    for account in accounts_with_threads:
        handle = account["handle"]
        thread_starters = account["thread_starters"]
        
        print(f"\n@{handle} ({len(thread_starters)} threads)...", end=' ', flush=True)
        
        try:
            # PASS 2: Get complete (threads + replies)
            data = client.user_posts_complete(handle, limit=40)
            complete_posts = data.get("tweets", data.get("data", []))
            
            # Extract from threads
            all_signals = []
            threads_extracted = []
            
            for post in complete_posts:
                # Check if this is part of a thread
                if post.get('is_thread') or post.get('thread_length', 0) > 1:
                    # Extract thread signals
                    thread_signals = classify_signal(
                        text=post.get('text', ''),
                        post_id=post.get('id', post.get('tweet_id', '')),
                        author_handle=extract_handle_from_post(post),
                        author_id=post.get('author_id', ''),
                        created_at=post.get('created_at', ''),
                        like_count=post.get('likes', post.get('like_count', 0)),
                        retweet_count=post.get('retweets', post.get('retweet_count', 0)),
                        reply_count=post.get('replies', post.get('reply_count', 0)),
                        quote_count=post.get('quote_count', 0),
                        bookmark_count=post.get('bookmark_count', 0),
                        is_thread=True,
                        thread_length=post.get('thread_length', 2),
                    )
                    all_signals.extend(thread_signals)
                else:
                    # Standalone post from complete
                    signals = classify_signal(
                        text=post.get('text', ''),
                        post_id=post.get('id', post.get('tweet_id', '')),
                        author_handle=extract_handle_from_post(post),
                        author_id=post.get('author_id', ''),
                        created_at=post.get('created_at', ''),
                        like_count=post.get('likes', post.get('like_count', 0)),
                        retweet_count=post.get('retweets', post.get('retweet_count', 0)),
                        reply_count=post.get('replies', post.get('reply_count', 0)),
                        quote_count=post.get('quote_count', 0),
                        bookmark_count=post.get('bookmark_count', 0),
                    )
                    all_signals.extend(signals)
            
            # Save
            new_s = save_signals(all_signals, handle)
            
            results["handles"][handle]["pass2_posts"] = len(complete_posts)
            results["handles"][handle]["pass2_signals"] = len(all_signals)
            results["total_signals_extracted"] += len(all_signals)
            results["total_threads_found"] += len(thread_starters)
            
            print(f"{len(complete_posts)} items, {len(all_signals)} signals")
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        time.sleep(0.3)
    
    results["total_cost_usd"] = client.total_cost
    results["handles_processed"] = len(handles)
    
    client.close()
    
    print(f"\n{'=' * 60}")
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Accounts processed: {results['handles_processed']}")
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
    
    print(f"Running smart pipeline for {len(handles)} accounts...")
    results = run_smart_pipeline(handles)
    
    # Save results
    output_file = DATA_DIR / "pipeline_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
