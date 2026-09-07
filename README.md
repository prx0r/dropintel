# DROPINTEL — Commerce Signal Intelligence

**Goal:** Find what agents actually pick and build what they want.

---

## Directory Structure

```
dropintel/
├── README.md                    # This file
├── BUILD_NOTES.md               # What we built today
├── HANDOVER.md                  # Next agent instructions
├── STATUS.md                    # Current status
├── synergy.md                   # Drop repo + X convergence
│
├── docs/
│   ├── intelligence/            # Research findings
│   │   ├── INSIGHTS.md         # Recent insights
│   │   ├── REPORT.md           # Complete intelligence report
│   │   ├── githubalpha.md      # GitHub infrastructure
│   │   ├── gitalpha2.md        # Deeper GitHub findings
│   │   ├── goblinalpha.md      # Full GitGoblin research
│   │   ├── google-ads-alpha.md # Google Ads engineers
│   │   ├── google-merchant-center.md # GMC goldmine
│   │   └── merchant-center-goldmine.md # Complete strategy
│   │
│   ├── thesis/                 # Business thesis
│   │   ├── 3biz.md            # 3-business thesis
│   │   ├── ALPHAdamn.md       # Complete thesis
│   │   ├── vision.md          # Why ChatGPT won't own everything
│   │   ├── smartbarbell.md    # Resolution Broker thesis
│   │   ├── geodrop-engine.md  # Installed-base ownership
│   │   └── thesis-definitive.md # Final thesis
│   │
│   └── dev/                    # Developer docs
│       ├── DEV_INSTRUCTIONS.md # Build instructions
│       └── getxapi-reference.md # GetXAPI usage
│
├── config/                      # Account configs
├── data/                        # Extracted signals, crossref, scores
├── output/                      # Daily briefs, reports
├── src/                         # Python extraction pipeline
└── tests/                       # Test files
```

---

## Quick Start

### Check X signals
```bash
python3 -c "import json; from pathlib import Path; signals = []; [signals.extend(json.load(open(f))) for f in Path('data/extracted').glob('*_signals_*.json')]; print(f'Total: {len(signals)}')"
```

### Query BigQuery
```bash
python3 -c "from google.cloud import bigquery; client = bigquery.Client(project='project-ff2366d2-8fda-4fcb-9ba'); print(list(client.list_tables('drop')))"
```

---

## Key Documents

| Document | Read This If... |
|----------|-----------------|
| `docs/thesis/thesis-definitive.md` | You want the final thesis |
| `docs/intelligence/REPORT.md` | You want all findings |
| `docs/dev/DEV_INSTRUCTIONS.md` | You want to build something |
| `HANDOVER.md` | You're the next agent |

---

*Last updated: 2026-09-07*
