# The Definitive Thesis — High-Certainty Agentic Commerce

**Date:** 2026-09-07
**Status:** VALIDATED — Refined and sharpened

---

## The One Sentence

> **Own the evidence-backed compatibility graph and live supplier state; use Merchant Center, Shopify Catalog, structured web data and eventually UCP/ACP as distribution rails.**

---

## The Moat

**The feeds themselves are not the moat.**

The moat is knowing, with unusually high certainty:

- **What the object is**
- **What fits it**
- **What does NOT fit it**
- **What superseded it**
- **Who actually has the correct replacement available now**

---

## The Correction

`related_product` is not a general installed-base compatibility graph. Google's relation points to other products in the merchant's inventory.

If you sell a Bosch pump but don't sell the 12-year-old Bosch dishwasher it fits, you cannot rely on `related_product` for the dishwasher→pump edge.

That edge belongs in **our canonical graph** and gets flattened outward into:

- `product_detail`
- Q&A
- Manuals
- PDP text/JSON-LD
- Images

`related_product` represents relations among products **we actually sell**: old part→new part, substitute→substitute, required accessory.

---

## The Internal Object

```
INSTALLED ASSET
Bosch SMS46MI08E
        │
        ├── has_part ────── Bosch 00631200
        │                       │
        │                       ├── superseded_by → 00651956
        │                       ├── voltage → 230V
        │                       ├── connector → X
        │                       └── incompatible_with → ...
        │
        ├── model_plate_location
        ├── production_years
        └── visual signatures

                         ↓ flatten

GOOGLE
brand + MPN
product_detail
question_and_answer
document_link
related_product
images/video
availability
price
local inventory

SHOPIFY
rich PDP
structured variants
Catalog
machine-readable inventory

WEB
JSON-LD
crawlable compatibility pages
manual/evidence pages
```

**Our private graph can be much richer than any one distribution protocol.**

---

## Where to Hunt First

| Rank | Market | Why | Verdict |
|------|--------|-----|---------|
| **1** | 🇫🇮 Allaway legacy central-vacuum parts | 250k+ homes, decades of legacy, serial/model dependence | **Exceptional** |
| **2** | 🇫🇮 Vallox legacy ventilation parts | Old units, OEM doesn't sell direct | **Exceptional** |
| **3** | 🇳🇴 Cabin water-system replacement | Enormous cottage base, pumps/valves with compatibility | **Very strong** |
| **4** | 🇫🇮 Heat-pump lifecycle electronics | 1.8m cumulative, aging controls/sensors | **Strong** |
| **5** | 🇳🇴/🇸🇪/🇫🇮 Automower legacy charging | Year/generation/amp ambiguity | **Great benchmark** |
| **6** | 🇫🇮 Helo/Tylö/Harvia legacy controls | ~3m sauna installed base | **Strong** |
| **7** | 🇳🇴 Jabsco/Johnson marine pump/impeller | Perfect "what is this?" photo problem | **Technically perfect** |
| **8** | 🇬🇧 EV charger aftersales parts | Large installed base, repair wave | **Excellent hybrid** |

**Country ranking:** Finland first, Norway second, Sweden third, UK fourth.

---

## Allaway Finland — The Cleanest First Campaign

**250,000+ Finnish homes** with central vacuum systems.

Current manufacturer discusses compatibility when replacing old KP/AW-series machines. Finnish wholesale catalogs contain hundreds of products oriented to trade purchasing, not consumer decision experience.

```text
SUPPLY:
warehouse ✓
inventory ✓
OEM relationships ✓
shipping ✓
30 years of SKUs ✓

CONSUMER:
"What Allaway do I have?"
"What replaced KP1200?"
"Does this hose fit my inlet?"
"Is this the old or new receiver?"
"What filter fits my 1992 unit?"
```

**Build:** Allaway Finder Finland — 10–15 historical machine families, 50–100 replacement SKUs.

---

## The Screening Formula

```text
HIGH_CERTAINTY_COMMERCE_SCORE =

installed_base
× replacement_frequency
× identity_difficulty
× compatibility_complexity
× supersession_complexity
× wrong_part_cost
× purchase_urgency
× supplier_stock_depth
× supplier_operational_quality
× digital_merchant_gap
× language_fragmentation
× visual_identifiability
× gross_margin
× shipping_suitability

÷ OEM_DTC_quality
÷ best_specialist_quality
÷ return_risk
÷ installation/safety_risk
```

**Key question:** Can we materially beat the single best seller on certainty?

---

## Supplier Requirements (Priority Zero)

```text
stock access                PASS
stable supplier SKU         PASS
wholesale economics         PASS
blind/direct shipping       PASS
dispatch SLA                PASS
returns/RMA                 PASS
stock freshness             PASS
consumer-safe packaging     PASS
```

**No warehouse, yes. No shipping operation, yes. No retail responsibility, no.**

---

## The Reusable Company

```
NICHE DISCOVERY
      ↓
OEM DOCUMENT INGEST
      ↓
ASSET/PART GRAPH
      ↓
VISUAL IDENTIFICATION DATASET
      ↓
SUPPLIER NORMALIZATION
      ↓
GMC + SHOPIFY + WEB
      ↓
TRANSACTION
      ↓
WRONG-PART / SUCCESS OUTCOME
      ↓
GRAPH IMPROVES
      ↓
CLONE INTO NEXT INSTALLED BASE
```

**Every launch leaves behind a reusable resolution engine.**

---

## The Distribution Priority

```
1. Google Merchant Center (conversational attributes)
2. Excellent crawlable PDP/JSON-LD
3. Google Images/Lens readiness
4. Shopify as commerce backend + Catalog
5. ChatGPT direct channel when Nordic eligibility expands
6. UCP/ACP/MCP later
```

---

## Local Inventory

Google's local inventory data supports store-level availability. Finland and Norway are supported markets.

```text
in_stock
local
dispatch_today
pickup_possible
supplier_confidence
```

**Supplier inventory synchronization is part of the recommendation advantage.**

---

## Feed Optimization Pattern

| Surface | Content |
|---------|---------|
| `product_detail` | Deterministic structured facts |
| `question_and_answer` | Ambiguities, negative compatibility, common questions |
| `document_link` | OEM manual, installation guide, parts diagram |
| `related_product` | Products **we sell** that are substitutes/required/accessories |
| MPN/brand/GTIN | Entity resolution |
| images | Visual identity and differentiators |
| video | Angles, connectors, model plate, physical recognition |

---

*Document saved: 2026-09-07*
