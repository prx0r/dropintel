"""BigQuery sync — store signals and crossref results.

Uses the existing 'drop' dataset in BigQuery.
Creates new tables for dropintel signals.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.cloud import bigquery


# ---------------------------------------------------------------------------
# BigQuery client
# ---------------------------------------------------------------------------

def get_client():
    """Get BigQuery client with credentials from vault."""
    with open('/root/.agent-vault/vault.json') as f:
        vault = json.load(f)
    
    creds = Credentials(
        token=None,
        refresh_token=vault['GOOGLE_REFRESH_TOKEN'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=vault['GOOGLE_CLIENT_ID'],
        client_secret=vault['GOOGLE_CLIENT_SECRET'],
    )
    creds.refresh(Request())
    
    return bigquery.Client(
        project=vault['GOOGLE_CLOUD_PROJECT'],
        credentials=creds,
    )


# ---------------------------------------------------------------------------
# Schema definitions
# ---------------------------------------------------------------------------

SIGNALS_SCHEMA = [
    bigquery.SchemaField("signal_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("post_id", "STRING"),
    bigquery.SchemaField("author_handle", "STRING"),
    bigquery.SchemaField("published_at", "TIMESTAMP"),
    bigquery.SchemaField("signal_type", "STRING"),
    bigquery.SchemaField("domain", "STRING"),
    bigquery.SchemaField("claim", "STRING"),
    bigquery.SchemaField("claim_quantitative", "BOOLEAN"),
    bigquery.SchemaField("sample_size", "STRING"),
    bigquery.SchemaField("methodology", "STRING"),
    bigquery.SchemaField("recommendation", "STRING"),
    bigquery.SchemaField("is_self_reported", "BOOLEAN"),
    bigquery.SchemaField("has_data", "BOOLEAN"),
    bigquery.SchemaField("is_thread", "BOOLEAN"),
    bigquery.SchemaField("thread_length", "INTEGER"),
    bigquery.SchemaField("thread_position", "STRING"),
    bigquery.SchemaField("is_reply", "BOOLEAN"),
    bigquery.SchemaField("conviction", "STRING"),
    bigquery.SchemaField("evidence_count", "INTEGER"),
    bigquery.SchemaField("extracted_at", "TIMESTAMP"),
]

CROSSREF_SCHEMA = [
    bigquery.SchemaField("claim_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("claim_text", "STRING"),
    bigquery.SchemaField("sources", "STRING", mode="REPEATED"),
    bigquery.SchemaField("evidence_strength", "INTEGER"),
    bigquery.SchemaField("validation_status", "STRING"),
    bigquery.SchemaField("first_seen", "TIMESTAMP"),
    bigquery.SchemaField("last_updated", "TIMESTAMP"),
]


# ---------------------------------------------------------------------------
# Sync functions
# ---------------------------------------------------------------------------

def sync_signals(client, signals: list[dict], table_id: str = "dropintel_signals"):
    """Sync signals to BigQuery."""
    dataset_id = "drop"
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    # Check if table exists, create if not
    try:
        client.get_table(full_table_id)
    except Exception:
        table = bigquery.Table(full_table_id, schema=SIGNALS_SCHEMA)
        table = client.create_table(table)
        print(f"Created table {full_table_id}")
    
    # Prepare rows
    rows = []
    for s in signals:
        row = {
            'signal_id': s.get('signal_id', ''),
            'post_id': s.get('post_id', ''),
            'author_handle': s.get('author_handle', '') if isinstance(s.get('author_handle'), str) else s.get('author_handle', {}).get('userName', ''),
            'published_at': s.get('published_at', ''),
            'signal_type': s.get('signal_type', ''),
            'domain': s.get('domain', ''),
            'claim': s.get('claim', '')[:1000],  # Truncate long claims
            'claim_quantitative': s.get('claim_quantitative', False),
            'sample_size': s.get('sample_size'),
            'methodology': s.get('methodology'),
            'recommendation': s.get('recommendation'),
            'is_self_reported': s.get('is_self_reported', True),
            'has_data': s.get('has_data', False),
            'is_thread': s.get('is_thread', False),
            'thread_length': s.get('thread_length', 1),
            'thread_position': s.get('thread_position', 'STANDALONE'),
            'is_reply': s.get('is_reply', False),
            'conviction': s.get('conviction', 'MEDIUM'),
            'evidence_count': s.get('evidence_count', 0),
            'extracted_at': s.get('extracted_at', datetime.now(timezone.utc).isoformat()),
        }
        rows.append(row)
    
    # Insert
    errors = client.insert_rows_json(full_table_id, rows)
    if errors:
        print(f"Insert errors: {errors}")
    else:
        print(f"Inserted {len(rows)} signals into {full_table_id}")
    
    return len(rows)


def sync_crossref(client, crossref: dict, table_id: str = "dropintel_crossref"):
    """Sync crossref results to BigQuery."""
    dataset_id = "drop"
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    
    # Check if table exists, create if not
    try:
        client.get_table(full_table_id)
    except Exception:
        table = bigquery.Table(full_table_id, schema=CROSSREF_SCHEMA)
        table = client.create_table(table)
        print(f"Created table {full_table_id}")
    
    # Prepare rows from corroborated claims
    rows = []
    for claim in crossref.get('corroborated_claims', []):
        row = {
            'claim_id': claim.get('claim_id', ''),
            'claim_text': claim.get('claim_text', '')[:1000],
            'sources': claim.get('sources', []),
            'evidence_strength': claim.get('evidence_strength', 0),
            'validation_status': claim.get('validation_status', 'UNCHECKED'),
            'first_seen': datetime.now(timezone.utc).isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat(),
        }
        rows.append(row)
    
    if rows:
        errors = client.insert_rows_json(full_table_id, rows)
        if errors:
            print(f"Insert errors: {errors}")
        else:
            print(f"Inserted {len(rows)} crossref claims into {full_table_id}")
    
    return len(rows)


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------

def run_bigquery_sync():
    """Run full BigQuery sync."""
    client = get_client()
    
    # Load all signals
    extracted_dir = Path(__file__).parent.parent.parent / 'data' / 'extracted'
    all_signals = []
    for f in extracted_dir.glob('*_signals_*.json'):
        with open(f) as fh:
            signals = json.load(fh)
            all_signals.extend(signals)
    
    print(f"Loaded {len(all_signals)} signals")
    
    # Sync signals
    sync_signals(client, all_signals)
    
    # Load crossref if exists
    crossref_path = Path(__file__).parent.parent.parent / 'data' / 'crossref' / 'claims_crossref.json'
    if crossref_path.exists():
        with open(crossref_path) as f:
            crossref = json.load(f)
        sync_crossref(client, crossref)
    
    print("BigQuery sync complete")


if __name__ == "__main__":
    run_bigquery_sync()
