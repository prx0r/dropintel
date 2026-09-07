"""Recursive graph walker — find accounts behind accounts.

Key insight from the research: "find Cobie behind Ansem"
The best alpha comes from low-follower accounts that high-signal accounts interact with.

This module:
1. Takes high-signal accounts
2. Finds who they reply to / quote / mention
3. Scores those accounts for signal quality
4. Returns the "accounts behind the accounts"
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .pipeline import GetXClient


# ---------------------------------------------------------------------------
# Graph walker
# ---------------------------------------------------------------------------

class GraphWalker:
    """Walk the X graph to find hidden high-signal accounts."""
    
    def __init__(self, client: GetXClient):
        self.client = client
        self.visited = set()
        self.candidates = {}  # handle -> stats
    
    def walk_from_account(self, handle: str, depth: int = 1, max_depth: int = 2):
        """Walk graph from an account, finding who they interact with."""
        if handle in self.visited or depth > max_depth:
            return
        
        self.visited.add(handle)
        print(f"{'  ' * depth}Walking @{handle}...")
        
        try:
            # Get recent posts
            data = self.client.user_posts(handle, limit=10)
            posts = data.get("tweets", data.get("data", []))
            
            for post in posts:
                text = post.get('text', '')
                
                # Find mentions and replies
                mentions = re.findall(r'@(\w+)', text)
                for mentioned in mentions:
                    if mentioned.lower() != handle.lower() and mentioned not in self.visited:
                        if mentioned not in self.candidates:
                            self.candidates[mentioned] = {
                                'handle': mentioned,
                                'mentioned_by': [],
                                'mention_count': 0,
                                'depth': depth,
                            }
                        self.candidates[mentioned]['mentioned_by'].append(handle)
                        self.candidates[mentioned]['mention_count'] += 1
                
                # Find quoted/retweeted users
                if post.get('is_quote') or post.get('is_retweet'):
                    original_author = post.get('quoted_tweet', {}).get('author', {})
                    if isinstance(original_author, dict):
                        orig_handle = original_author.get('userName', '')
                        if orig_handle and orig_handle.lower() != handle.lower():
                            if orig_handle not in self.candidates:
                                self.candidates[orig_handle] = {
                                    'handle': orig_handle,
                                    'mentioned_by': [],
                                    'mention_count': 0,
                                    'depth': depth,
                                }
                            self.candidates[orig_handle]['mentioned_by'].append(handle)
                            self.candidates[orig_handle]['mention_count'] += 1
            
            # Recurse into high-mention accounts
            if depth < max_depth:
                top_mentions = sorted(
                    self.candidates.values(),
                    key=lambda x: x['mention_count'],
                    reverse=True
                )[:5]
                
                for candidate in top_mentions:
                    if candidate['handle'] not in self.visited:
                        self.walk_from_account(candidate['handle'], depth + 1, max_depth)
        
        except Exception as e:
            print(f"{'  ' * depth}  Error: {e}")
    
    def score_candidates(self) -> list[dict]:
        """Score discovered accounts for signal potential."""
        scored = []
        
        for handle, stats in self.candidates.items():
            # Skip if already in our registry
            # Score based on:
            # - mention count (high = important to influential accounts)
            # - depth (shallower = more directly connected)
            # - follower count (we want low-follower high-signal)
            
            score = stats['mention_count'] * 10
            score += (3 - stats['depth']) * 5  # Prefer shallower
            
            stats['score'] = score
            scored.append(stats)
        
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def discover_new_accounts(self, seed_handles: list[str], max_depth: int = 2) -> list[dict]:
        """Discover new accounts from seed handles."""
        for handle in seed_handles:
            self.walk_from_account(handle, depth=1, max_depth=max_depth)
        
        return self.score_candidates()


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_graph_walk(seed_handles: list[str] = None):
    """Run graph walk from high-signal accounts."""
    if seed_handles is None:
        # Use our top accounts as seeds
        seed_handles = [
            'kurtinc',
            'igrigorik',
            'Romain_Lapeyre',
            'iPullRank',
            'gilgNYC',
        ]
    
    client = GetXClient()
    walker = GraphWalker(client)
    
    print(f"Walking graph from {len(seed_handles)} seed accounts...")
    new_accounts = walker.discover_new_accounts(seed_handles, max_depth=2)
    
    client.close()
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'crossref'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'graph_walk.json'
    output = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'seed_accounts': seed_handles,
        'discovered': len(new_accounts),
        'accounts': new_accounts[:20],  # Top 20
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n=== DISCOVERED {len(new_accounts)} NEW ACCOUNTS ===")
    for acc in new_accounts[:10]:
        print(f"  @{acc['handle']}: score={acc['score']}, mentioned by {', '.join(acc['mentioned_by'][:3])}")
    
    return output


if __name__ == "__main__":
    run_graph_walk()
