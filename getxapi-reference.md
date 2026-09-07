# GetXAPI Scraper Reference

## Overview

GetXAPI is the cheapest X/Twitter data provider at $0.05/1k tweets. Used in the BEAR project for social signal extraction.

**Base URL:** `https://api.getxapi.com/twitter`
**Auth:** `Authorization: Bearer {api_key}`
**Max per request:** 20 tweets
**Free credit:** $0.10 on signup

---

## Methods

### 1. Advanced Search

```python
from bear.social.providers.getxapi import GetXAPI
from datetime import datetime

api = GetXAPI(api_key="your-key")

results = api.search(
    query="bitcoin lang:en",
    limit=20,
    since=datetime(2026, 8, 1),
    until=datetime(2026, 8, 15),
    cursor=""
)
```

**Params:**
- `q` — search query (supports Twitter advanced search syntax)
- `product` — "Latest" or "Top"
- `count` — max 20
- `since_time` — `YYYY-MM-DD_HH:MM:SS_UTC`
- `until_time` — `YYYY-MM-DD_HH:MM:SS_UTC`
- `cursor` — for pagination

**Endpoint:** `/tweet/advanced_search`

### 2. User Posts

```python
results = api.user_posts(
    username="elaboratecohen",
    limit=20,
    cursor=""
)
```

Uses `from:{username}` query under the hood.

### 3. Get Single Post

```python
tweet = api.get_post(tweet_id="1234567890")
```

**Endpoint:** `/tweet/get`

### 4. Get Thread

```python
thread = api.get_thread(tweet_id="1234567890", limit=20)
```

Walks `in_reply_to_status_id_str` to reconstruct full thread.

### 5. Get Replies

```python
replies = api.get_replies(tweet_id="1234567890", limit=20)
```

Uses `conversation_id:{tweet_id}` query.

---

## Response Format

```python
SearchResponse(
    tweets=[Tweet, Tweet, ...],
    next_cursor="abc123",
    has_next=True,
    provider="getxapi",
    cost_usd=0.001
)
```

### Tweet Object

```python
Tweet(
    id="1234567890",
    text="tweet content",
    author="username",
    author_name="Display Name",
    created_at=datetime(...),
    likes=42,
    retweets=10,
    replies=5,
    views=1000,
    url="https://x.com/...",
    raw={...}  # original API response
)
```

---

## Pagination

```python
# First page
results = api.user_posts("username", limit=20)

# Check if more
if results.has_next:
    # Next page
    next_results = api.user_posts("username", cursor=results.next_cursor)
```

---

## Cost Tracking

Every response includes `cost_usd`:
```python
total_cost = sum(r.cost_usd for r in all_responses)
```

**Cost per source:** ~$0.005 (5 API calls for full month)

---

## Rules (from BEAR AGENTS.md)

1. **Raw Before Filter** — Store everything, filter during analysis
2. **Budget-First** — Check dedup → check balance → fetch → log → review
3. **Log Every Call** — Append to `budgets/fetch_log.jsonl`
4. **Never Hardcode Keys** — Use `.env` file

---

## Environment Setup

```bash
# .env
GETXAPI_KEY=get-x-api-xxxxxxxxxxxx
GETXAPI_KEY_BACKUP=get-x-api-yyyyyyyyyyyy
```

```python
import os
api = GetXAPI(api_key=os.environ["GETXAPI_KEY"])
```

---

## Reconnection Procedure

If primary key fails:
1. Try backup key: `GETXAPI_KEY_BACKUP`
2. Check balance at getxapi.com dashboard
3. If exhausted, wait for monthly reset or add funds

---

## Data Pipeline

```
GetXAPI response → raw JSON.zst → normalize → posts.parquet → derived views
```

Never throw away paid data. Store raw, filter for analysis.
