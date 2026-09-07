# Git Alpha 2 — The Algorithm Layer

**Date:** 2026-09-07
**Status:** VALIDATED — Decision functions now visible in public code

---

## Executive Summary

The biggest discovery is that the useful alpha is **not merely "engineers building agentic commerce."** We can now see several actual decision functions in public code.

The strongest new artifact is **Shopify's own agent-facing Global Catalog instructions**. It publicly tells an agent what should be treated as a hard exclusion versus a soft ranking signal. Combined with Anthropic's open ranker, NVIDIA's recommendation pipeline, Timefold's scheduler, and Probook's public dispatch features, we can reconstruct a surprisingly complete Agent Commerce / Supplier OS architecture.

---

## The GitHub ↔ X Hidden-Goat Graph

| Person | Public identity | GitHub | Why they matter |
|--------|-----------------|--------|-----------------|
| **Gil Greenberg** | **X @gilgNYC** | **gil--** | My best new find. Shopify engineer; open-sourced an iMessage shopping agent actually exercised against real merchants. Also contributes directly to Shopify's UCP tooling. |
| **Ilya Grigorik** | **X @igrigorik** | **igrigorik** | Central Shopify/UCP architect. Following his PRs/replies exposes capabilities before normal ecommerce discourse catches up. |
| **Ali Shazal** | LinkedIn verified; X unresolved | **alishazal** | Committer on Anthropic's new `commerce-agents` repo and co-author of Anthropic's production commerce-agent playbook. |
| **Matthew Koen** | LinkedIn verified; X unresolved | unresolved | Anthropic Applied AI; co-author of commerce-agent blueprint. Publicly discusses production workflows involving appointments/revenue/automation. |
| **Geoffrey De Smet** | **X @GeoffreyDeSmet** | **ge0ffrey** | Timefold CTO / OptaPlanner creator. This is the optimization layer beneath a Probook-like dispatch brain. |
| **Jing Li** | social unresolved | **jingyli** | Google/UCP contributor behind Location/serviceability capabilities relevant to local services. |
| **Lee Hwa** | social unresolved | **lhwa** | Meta contributor to ACP proposals around product feeds, feed provenance and pricing. |
| **Alex Springer** | OpenAttribution public identity | **jalexspringer** | Building the attribution layer for recording what content agents retrieved/cited before a transaction. |
| **Radovan Synek** | blog/LinkedIn | **rsynek** | Timefold routing/optimization engineer; very relevant to field-service scheduling. |
| **Lukáš Petrovický** | public professional profile | **triceo** | Core Timefold solver engineer. |
| **Antonio Martinez** | LinkedIn/NVIDIA verified | NVIDIA blueprint contributor | Working directly on NVIDIA's open agentic-retail recommendation/search implementation. |
| **George Eliadis** | **X @georgeprobook** | unresolved | Probook founder. Public signal is extraordinary; actual dispatcher code appears private. |
| **Lewis Zhang** | LinkedIn verified | unresolved | Probook CTO. Particularly interesting because he previously worked on Roblox player/server matching. |

I deliberately rejected several apparent handle matches because I couldn't verify identity.

---

## 1. Gil Greenberg Is the New Hidden Goat

Following **Ilya → X activity → Gil → GitHub** produced the GitGoblin pattern.

Gil's repo `gil--/ucp-agent-imessage` is an invite-only iMessage shopping-agent proof of concept. The README says it **runs and has been exercised against real merchants**.

### Architecture

```
DISCOVER
Shopify Global Catalog
anonymous
    ↓
CART
merchant-specific
reversible
    ↓
CHECKOUT
agent credential
reviewable
    ↓
PURCHASE
buyer-linked Shop credential
exact amount approval
idempotent
```

The LLM **doesn't own the transaction**.

Gil explicitly separates:

```
MODEL
interpret intent
compare products
propose tools
recommend

    ↓

DETERMINISTIC APPLICATION
trusted product provenance
merchant identity
cart state
checkout state
budget
payment credential
authorization
exact-total approval
purchase completion
```

**Key insight:** Use the LLM for fuzzy matching/reasoning. Never use it as the ledger or authorization system.

---

## 2. Shopify Published an Agent SEO Operator Manual

Shopify's public `Shopify/ucp-cli` contains a skill designed for agents using the Global Catalog.

### Soft ranking context

```
intent
country
region
postal code
currency
language
eligibility
```

These **inform ranking/localization**, rather than excluding a candidate.

### Hard filters

```
price
availability
ships_to
ships_from
condition
taxonomy/category
product attributes
ratings
price tier
```

Candidates failing these are excluded.

### The documented query structure

```json
{
  "query": "marathon training shoes",
  "context": {
    "intent": "daily trainer for marathon training",
    "address_country": "US",
    "currency": "USD",
    "language": "en-US"
  },
  "filters": {
    "price": {"max": 15000},
    "available": true,
    "ships_to": {"country": "US"},
    "attributes": [
      {"name": "Size", "values": ["10", "10.5"]}
    ],
    "rating": {
      "variant": {
        "min": 4.5,
        "min_count": 10
      }
    },
    "price_tier": ["low", "medium"]
  }
}
```

### The agent is told to retain

```
seller
price
rating
rating count
top features
availability
running-low status
native-checkout eligibility
shipping requirements
```

### The pagination insight

Shopify explicitly tells the agent:

> **Pagination gives more of the same ranking.**

If results aren't satisfying intent, **change the query first**—synonyms, narrower/broader terms, brand names—rather than blindly paging.

That means a shopping agent is already being taught:

```
intent
    ↓
translate to catalog vocabulary
    ↓
retrieve
    ↓
bad candidate set?
 ├─ yes → reformulate query
 └─ no
      ↓
hard filters
      ↓
reason about survivors
```

---

## 3. Anthropic Published a Reference Ranking Function

`anthropics/commerce-agents` — official Anthropic reference implementation.

### Text-field weighting

```
title        3.0
brand        2.0
category     2.0
attributes   1.5
description  1.0
```

### The algorithm

```
apply hard filters
      ↓
calculate relevance
      ↓
remove score == 0
      ↓
best_score = highest candidate

keep only:
candidate_score >= best_score × 0.50
      ↓
try soft filters
      ↓
if soft filters remove everything:
    abandon them
      ↓
sort by relevance
      ↓
rating breaks relevance ties
```

### The query rewriting insight

Anthropic's higher-level search skill tells an agent to:

```
extract:
budget
recipient
dates
size
intended use
dealbreakers

then:

USER STATED constraint
        ↓
hard filter

ASSUMED preference
        ↓
search/query wording
```

And critically:

> phrase the request in **catalog vocabulary**, rather than preserving the customer's wording.

---

## 4. NVIDIA Exposes a Sophisticated Recommender

NVIDIA's public `Retail-Agentic-Commerce` implementation.

### Architecture

```
USER/CART
   ↓
EMBEDDING RETRIEVAL
top K candidates
   ↓
┌────────────────────┐
│                    │
▼                    ▼
USER              NLI
UNDERSTANDING      ALIGNMENT
AGENT              AGENT
│                    │
└──────────┬─────────┘
           ↓
     CONTEXT SYNTHESIS
           ↓
       ITEM RANKER
           ↓
   DETERMINISTIC GUARD
```

### Candidate intent score

```
0.8 – 1.0   strong fit
0.4 – 0.7   moderate fit
0.0 – 0.3   weak fit
```

Primary candidates must be:

```
alignment_score > 0.7
AND
product not already in cart
```

If fewer than 3 survive, it backfills the highest remaining scores.

### Final priority

```
1. CROSS-SELL FIT
2. ALIGNMENT SCORE
3. DIVERSITY
```

### Deterministic validation

```
product exists
stock > 0
margin acceptable
not already in cart
```

**Key insight:** fuzzy intelligence inside; deterministic commerce constraints outside.

---

## 5. NVIDIA Open-Sourced a Promotion Decision Function

### Precomputed signals

```
inventory pressure
competitive pricing position
seasonality
product lifecycle
demand velocity
allowed margin-safe actions
```

### Decision table

| Condition | Action |
|-----------|--------|
| Low inventory | No promo |
| High inventory + already below market | None / free shipping |
| High inventory + at market | 5% |
| High inventory + above market | 10% |

### Modifiers

```
peak/post-season → discount +1 tier
pre-season       → free shipping
clearance        → discount +1
new arrival      → reduce to free shipping
demand slowing   → discount +1
demand rising    → discount -1
```

The server has already removed any actions violating margins. The LLM merely chooses among **safe actions**.

---

## 6. Connect Probook to Timefold

Probook's code appears private. But public descriptions reveal its optimization problem.

### Probook's dispatcher considers

```
technician skill / experience
geography
availability
historical performance
conversion / close rate
ticket size
job type
job priority
customer context
equipment context
ETA
forecasted revenue
```

### Timefold's constraint hierarchy

```
HARD
────
capacity
must finish before end time

MEDIUM
──────
maximize jobs assigned

SOFT
────
minimize driving time
```

### Field-service expansion

```
skills
priorities
technician affinity
fairness
dependencies
time windows
working hours
travel
```

### Reconstructed Probook-like objective

```
FIRST: FEASIBILITY

eligible(job, tech) =
    skills / license fit
    ∧ service area
    ∧ availability
    ∧ schedule feasibility
    ∧ equipment / job requirements

THEN OPTIMIZE:

score(job, tech) ≈

 + w1 × P(conversion | technician, job)
 + w2 × expected_ticket_value
 + w3 × skill_fit
 + w4 × customer/technician affinity

 - w5 × travel_time
 - w6 × predicted lateness
 - w7 × schedule disruption

 + w8 × job_priority
 + w9 × utilization/fairness
```

**That formula is a reconstruction, not leaked Probook code.** But all ingredients are supported by public descriptions.

---

## 7. Business Arena Is Another GitHub Find

Alibaba/Accio team released `CommerceAgentBench` and `BusinessArena`.

### CommerceAgentBench evaluates

```
supplier analysis
product publishing
logistics
Shopify operations
API/MCP workflows
public-web research
business documents
```

### Business Arena makes an AI operate a seller business for 30 simulated days

```
source products
allocate capital
enter markets
price
advertise
replenish
negotiate
handle customers
stay compliant
react to demand
react to competitors
```

### Economic equation

> business value is shaped by **deployed capital × capital turnover × realized margin**.

---

## 8. The Canonical Algorithm Is Emerging

Across **independent implementations from Shopify, Anthropic, NVIDIA, Timefold and Probook**:

```
                USER INTENT
                    │
                    ▼
           QUERY NORMALIZATION
                    │
                    ▼
          HARD ELIGIBILITY GATE
        ┌───────────┼────────────┐
        │           │            │
      stock       price       location
     service      skills       shipping
      area        variant      deadlines
        └───────────┼────────────┘
                    ▼
             CANDIDATE REMARK
         lexical / embedding / graph
                    │
                    ▼
             RELEVANCE PRUNE
                    │
                    ▼
          MULTI-OBJECTIVE RANK
        ┌───────────┼───────────┐
      intent      quality      value
       fit         trust       price
        │           │           │
      margin     delivery     diversity
        └───────────┼───────────┘
                    ▼
          DETERMINISTIC GUARD
                    │
                    ▼
            HUMAN/AGENT CHOICE
                    │
                    ▼
           AUTHORIZATION GATE
                    │
                    ▼
              TRANSACTION
                    │
                    ▼
              OUTCOME DATA
                    │
                    └─────────────► learning
```

That is **Supplier OS**.

Not "LLM does everything."

But **constraint solver + retrieval/ranker + prediction models + state machine + LLM reasoning around the ambiguous edges.**

---

## 9. This Changes the Agent SEO Thesis

### For a product merchant

```
title / canonical entity
brand
taxonomy
variant attributes
exact compatibility
price
availability
seller identity
ships_to
ships_from
rating + count
language
currency
locality
product features
native-checkout capability
```

### For a service supplier

```
service taxonomy
service area
skills
licenses
job compatibility
availability
capacity
price/rate
historical conversion
historical job value
travel/ETA
ratings/trust
equipment expertise
booking capability
payment capability
```

The first battle isn't persuasive copy. It's:

> **Can the agent prove this supplier/product is an eligible candidate?**

Then:

> **Is there enough structured evidence to rank it confidently?**

Then:

> **Can the agent transact without breaking the flow?**

---

## The Five Repos to Ingest Into GitGoblin

```
Shopify/ucp-cli
anthropics/commerce-agents
gil--/ucp-agent-imessage
NVIDIA-AI-Blueprints/Retail-Agentic-Commerce
TimefoldAI/timefold-quickstarts
```

## Repos to Watch

```
Universal-Commerce-Protocol/ucp
agentic-commerce-protocol/agentic-commerce-protocol
Accio-org/CommerceAgentBench
Accio-org/BusinessArena
agentcommercekit/ack
openattribution-org/*
```

## Highest-Alpha Signals

Diffs that change:

```
ranking fields
filter semantics
constraint weights
search context
eligibility
trust/provenance
personalization
price/availability freshness
merchant identity
checkout capability
dispatch objective
attribution
```

**New GitGoblin mode: `ALGO_SURFACE_CHANGED`**

---

## Crawl Log

1. Started from **@georgeprobook → Probook → founder/team pages → Sequoia profile → Lewis Zhang**
2. Confirmed Summers autonomous-booking claim; found **2,542 vs 2,873 discrepancy**
3. Extracted Probook's publicly disclosed dispatcher features
4. Searched Probook/Lewis GitHub; no verified public backend found
5. Pivoted through UCP/ACP protocol engineers
6. Followed **Ilya's X activity → Gil Greenberg**
7. Found `gil--/ucp-agent-imessage`; inspected real-merchant architecture
8. Followed Gil into **`Shopify/ucp-cli`**
9. Opened agent skill and Global Catalog reference; found **soft-context vs hard-filter split**
10. Opened **`anthropics/commerce-agents`**; extracted reference search ranker
11. Traced commit to **Ali Shazal**, then Anthropic's commerce article
12. Followed into **NVIDIA Retail Agentic Commerce**
13. Located recommendation YAML and extracted **0.7 cutoff, NLI bands**
14. Found NVIDIA's promotion arbiter and decision table
15. Followed Probook optimization problem into **Timefold**
16. Opened real ConstraintProvider and extracted solver hierarchy
17. Followed Timefold's maintainers to **Geoffrey De Smet / Radovan Synek**
18. Opened Alibaba's **CommerceAgentBench + BusinessArena**
19. Checked ACK/OpenAttribution as adjacent identity/trust layer

---

*Document saved word for word from research session.*
