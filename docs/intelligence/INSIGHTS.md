# Recent Insights — 2026-09-07

## The Shift That Just Happened

**Shopify Catalog is now the default product discovery layer for AI agents.**

When someone asks ChatGPT "find me a replacement pump for my Bosch SMS46MI08E":

```
ChatGPT → searches Shopify Catalog (billions of products)
       → finds matching products
       → shows to user
       → user buys
```

**If you're not in Shopify Catalog, you don't exist to agents.**

---

## UCP: The New Standard

**Universal Commerce Protocol** — co-developed by Shopify + Google.

| Partner | Role |
|---------|------|
| Shopify | Co-developer, reference implementation |
| Google | Co-developer, first buyer-side implementation |
| Etsy, Target, Walmart, Wayfair | Early partners |
| Amazon, Meta, Microsoft, Stripe, Visa | Endorsed |

**20+ partners. Open standard. Already shipping.**

---

## How Agent Discovery Works

### Two-Layer System

```
Layer 1: SHOIFY CATALOG (ranks first)
    ↓
Layer 2: AI AGENT (re-ranks on its own logic)
```

You optimize Layer 1. The agent controls Layer 2.

### Five Listing-Quality Signals

| Signal | What It Measures |
|--------|------------------|
| Description completeness | Full, specific product copy |
| Image coverage | Visual representation |
| Product reviews | Presence and depth |
| Variant completeness | Sizes, colors, options |
| Shop policy completeness | Shipping, returns |

### Hard Filters (Pass/Fail)

- Price range
- Availability (in stock)
- Shipping eligibility
- Product condition

**Fail a hard filter = REMOVED before ranking.**

---

## The Critical Insight: Inferred vs Stated

**Shopify's Catalog INFERS attributes it doesn't find explicitly.**

> "Half of what an agent reads about your product can be something Shopify's model guessed."

**If you state it as a metafield, the agent reads what YOU wrote.**

```
Shopify infers: "material: cotton" (maybe wrong)
You state: "material: organic cotton, 180gsm" (exact)
Agent reads: YOUR version
```

---

## What Shopify Does Automatically

For eligible US merchants (since March 2026):
- ✅ Products syndicated to ChatGPT, Copilot, Google
- ✅ `/products.json` served
- ✅ `/agents.md` generated
- ✅ Real-time price/inventory updates
- ✅ Category taxonomy mapping

**You don't need to opt in. You're already in.**

---

## The Checklist (What YOU Control)

### 1. Product JSON-LD on Every PDP

```html
<script type="application/ld+json">
{
  "@type": "Product",
  "name": "Bosch 00631200 Circulation Pump",
  "gtin13": "4005165123456",
  "offers": {
    "@type": "Offer",
    "price": "1129.00",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

### 2. GTIN Coverage

Every variant needs a barcode (UPC/EAN/ISBN).

### 3. Category Taxonomy

Use leaf nodes:
```
❌ "Electronics"
✅ "Electronics > Home Appliances > Dishwashers > Replacement Parts"
```

### 4. Reviews as Schema

Surface reviews as `aggregateRating` in JSON-LD.

### 5. Descriptions That Answer Questions

```
❌ "High quality pump"
✅ "Bosch 00631200. Compatible with SMS46MI08E. 230V. Ships Oslo, 2-day."
```

---

## The Ranking Formula

```
PRESENCE (are you in the catalog?)
    ↓
IDENTITY (can agents uniquely identify your product?)
    ↓
TRUST (reviews, ratings, brand authority)
    ↓
PRESENTATION (how your card renders)
```

**Miss presence = invisible**
**Miss identity = long-tail only**
**Miss trust = always ranked below competitors**

---

## The "Agentic Buy Box"

Multiple stores selling the same product → agent clusters → picks ONE.

**Winning factors:**
- Price
- Shipping coverage
- Availability
- Data richness

---

## What X Alpha Confirmed

| Finding | Source |
|---------|--------|
| AI traffic up 3x YoY, converts 2x | @Romain_Lapeyre (Shopify earnings) |
| ChatGPT driving 2.1% of revenue | @kurtinc (Shopify data) |
| 49% of merchants using MCP | @Romain_Lapeyre (Gorgias data) |
| Probook: 2,542 jobs/month, zero human | @georgeprobook (direct) |
| Wilson: $4.8M → $53M in 6 years | @WilsonCompanies (direct) |

---

## What GitHub Alpha Confirmed

| Finding | Source |
|---------|--------|
| UCP Location search/serviceability | GitHub PR (Aug 25, 2026) |
| Response-carried request constraints | GitHub PR (Aug 20, 2026) |
| ACP Product Feeds API | GitHub PR (Apr 17, 2026) |
| Content attribution proposal | GitHub Issue #180 |

---

## The Three-Business Thesis (Validated)

```
1. AGENT-NATIVE COMMERCE
   replacement parts, compatibility-heavy products
   → Build on Shopify, feed into Catalog

2. AGENT-NATIVE SERVICES
   EV installation, heat pumps, HVAC
   → Build supplier OS, get into service graph

3. AGENT-NATIVE SUPPLIER OS
   voice receptionist, CRM, booking
   → Free tool → data flywheel → platform lock-in
```

---

## The Competitive Landscape

| Company | What | Funding | Status |
|---------|------|---------|--------|
| Probook | AI OS for home services | $40M | Live |
| Avoca AI | AI receptionist | $125M | Live |
| Kebra (YC S26) | Field → asset memory | YC | Early |
| Lokuli/BookingClaw | Agent-native services | Unknown | Live in LA |

**UK/European market is empty.**

---

## The Timing

- UCP Location search shipped **August 25, 2026**
- Google AI Mode checkout **rolling out now**
- ChatGPT shopping **live for millions**
- W3C workshop **tomorrow (Sept 8-9)**

**The window is open.**

---

## Recommended Actions

### This Week
1. Build replacement-parts store on Shopify
2. Feed compatibility data into Catalog
3. Set up GitHub watch for UCP/ACP

### This Month
4. Launch EV charger service graph
5. Onboard 10 installers
6. Build compatibility engine

### This Quarter
7. Expand to heat pumps
8. Launch in Norway/Denmark
9. Sell the compatibility layer

---

## Key Metrics to Track

| Metric | Target |
|--------|--------|
| Products in Catalog | 100+ |
| JSON-LD coverage | 100% |
| GTIN coverage | 90%+ |
| Agent-driven revenue | >5% of total |
| Installer onboarded | 50+ |

---

*Generated: 2026-09-07*
*Sources: X alpha (505 signals) + Drop repo (1,661 observations) + GitHub (UCP/ACP tracking)*
