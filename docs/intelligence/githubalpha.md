# GitHub Alpha — The Infrastructure Layer Nobody's Watching

**Date:** 2026-09-07
**Status:** VALIDATED — GitHub review comments are more valuable than 99.9% of ecommerce Twitter

---

## Executive Summary

GitHub is absolutely alpha for this thesis, but the alpha is not "find cool repos." It is:

> **PRs → RFC/SEP proposals → review comments → maintainers → referenced issues → contributors from adjacent companies → implementation repos.**

That gets you underneath X. On X, people say "agentic commerce is coming." On GitHub, a Google engineer and a Shopify engineer are arguing over exactly what an agent is allowed to infer about whether a business can service an address.

---

## 1. The EV-installer idea is freakishly close to what UCP just shipped

On **August 25, 2026**, UCP merged a generic Location capability.

Not "find a retail store." A cross-vertical **Location Search + Lookup** primitive designed to answer things like:
- find locations near X
- determine whether a location **serves this buyer address**
- filter by hours
- filter by amenities
- filter by things currently available there

The original capability was authored by **Jing Li at Google** and merged by **Ilya Grigorik at Shopify**.

Then Ilya made the abstraction explicitly cross-vertical.

The critical sentence in the implementation is that an `item` can represent a:

> product variant, dish, **appointment-based service**, ticket, or another orderable item.

Your EV installation could conceptually become:

```
Business:
    EV-Install UK

Location:
    Nottingham installer branch / contractor

Item:
    residential_ev_charger_installation

Search:
    serves:
        NG7 2RD

    filters.items:
        residential_ev_charger_installation

    filters.amenities:
        ozEV_approved
        in_person_installation

Result:
    installer/service location capable of providing it
```

And UCP explicitly separates the later stages:

```
LOCATION → Find places that can currently provide the item
CATALOG → Identify / describe the service
CART → Concrete configuration + quantity
CHECKOUT + FULFILLMENT → price, eligibility, method, appointment/window, terms
```

That's essentially the architecture we independently arrived at.

---

## 2. Businesses can dynamically tell the agent what information they need

Ilya merged **response-carried request constraints** on August 20.

The problem: Static APIs can say `phone_number` is optional. But in this particular transaction, perhaps the business can't proceed without it.

So the business can return a machine-readable constraint:

```json
{
  "ucp": {
    "request_constraints": {
      "required": ["billing_address"]
    }
  }
}
```

Now translate that to EV installation:

```
User: "Get an EV charger installed."

Agent:
→ finds Nottingham installer
→ installer says it serves NG7
→ starts installation request

Business returns:
    required:
        charger_model
        property_type
        off_street_parking
        fuseboard_photo
        cable_distance
        property_ownership

Agent:
→ asks customer only missing questions
→ submits photos/details
→ receives quote/options
→ user approves
→ appointment booked
```

The **agent dynamically negotiates the form**.

---

## 3. ACP confirms the PRODUCT FEED is becoming an agent acquisition channel

The OpenAI/Stripe ACP repo merged its Product Feeds API on **April 17, 2026**.

It defines:

```
POST  /feeds
GET   /feeds/{id}
GET   /feeds/{id}/products
PATCH /feeds/{id}/products
```

And a canonical product representation containing:
- product/variant IDs
- descriptions
- pricing
- availability
- barcodes
- media
- options
- categories
- seller
- marketplace
- measurements
- unit pricing

**"Feed quality becomes SEO"** is not just an analogy anymore. They're literally creating the feed ingestion protocol.

---

## 4. Meta engineers are already worrying about feed freshness

**Lee Hwa (`lhwa`)**, contributing from Meta, proposed `suggested_price`.

The scenario:
1. merchant publishes £59.99 through its feed
2. agent indexes it
3. merchant price changes
4. user asks agent to buy
5. agent still thinks price is £59.99

The proposed checkout structure carries:

```
price = £59.99

source:
    feed_id
    feed_update_id
    feed_updated_at
    channel

observed_at:
    exact time agent observed price
```

**Agent-native merchants should optimize freshness, not merely richness.**

---

## 5. UCP Issue #180 — "WHY DID THE AGENT PICK ME?"

Proposed `match_factors`:

```
specification_match
rating
price
availability
location
delivery_speed
brand_preference
past_purchase
promotion
sustainability
relevance
```

This is explicitly motivated by merchants wanting to know why agents selected their product and how to optimize their feeds.

---

## 6. Content attribution — Google Analytics for agent decisions

**Alex Springer / OpenAttribution** proposed ACP `content_attribution`.

Imagine ChatGPT does:

```
retrieve:
  bosch.com/product...
  reddit.com/r/appliancerepair/...
  test.no/bosch-pump-review
  ourshop.no/bosch-00631200

cite:
  test.no/...
  ourshop.no/...

recommend:
  ourshop.no

checkout:
  £87
```

The proposed protocol can attach:

```json
{
  "content_retrieved": [...],
  "content_cited": [...]
}
```

**Google Analytics for agent decisions.**

---

## 7. What agent commerce loses sales over

Another ACP thread defines machine-readable cancellation/intent traces:

```
price_sensitivity
shipping_cost
shipping_speed
product_fit
trust_security
returns_policy
payment_options
comparison
timing_deferred
```

---

## 8. UCP semantics: hard constraints beat clever copy

When searching locations, UCP distinguishes between:

### HARD structured predicates
- serves this address
- within this radius
- has these items
- open at this time
- has required amenities

### Soft ranking hints
- free text
- context
- signals

The latter can affect ranking. But they **cannot override failed structured constraints**.

So: **Better prompt-engineered prose cannot turn an ineligible merchant into an eligible merchant.**

### Agent SEO Ranking Model

```
STAGE 1 — ELIGIBILITY
Can the merchant actually satisfy request?

STAGE 2 — CONFIDENCE
How certain is the model about that?

STAGE 3 — QUALITY
price / rating / policies / delivery / trust

STAGE 4 — PREFERENCE
brand / aesthetics / personalization

STAGE 5 — TRANSACTIONABILITY
Can agent actually complete it?
```

For compatibility-heavy goods and standardized services, we have a realistic shot at dominating stages **1 + 2 + 5**.

---

## 9. The hidden engineers watch graph

| Engineer | Company | Why Watch |
|----------|---------|-----------|
| **Jing Li (`jingyli`)** | Google | #1 sleeper. Designed Location search/serviceability |
| **Ilya Grigorik (`igrigorik`)** | Shopify | Control-plane GOAT. Governance + core UCP architecture |
| **Lee Hwa (`lhwa`)** | Meta | Pricing provenance, feeds, fulfillment, checkout |
| **Maxime Najim (`maximenajim`)** | Target | Deep protocol/security/error semantics |
| **Daniel Wyckoff** | Shopify | Core UCP shopping/payments architect |
| **Amit Handa** | Google | UCP governance + multiple vertical councils |
| **Aravind Rao** | — | ACP Product Feeds and promotions |
| **Rahul Bansal** | — | ACP feed infrastructure |
| **Alex Springer (`jalexspringer`)** | OpenAttribution | "Which agent-read content drove purchase?" |
| **Vignesh Sreedhar** | Meta | Product identity/canonical URL ambiguity |
| **Imran Hoosain** | Etsy | UCP Shopping Tech Council |
| **Prasad Wangikar** | Stripe | Payment/checkout protocol intersection |
| **Ryan Kelly** | PayPal | Product deep links for answer engines |
| **Prateek Srivastava** | commercetools | Store/location inventory + agent retail flows |

UCP's Shopping Tech Council includes: **Google, Shopify, Etsy, Meta, Amazon, Target, Microsoft, Stripe, Salesforce, Wayfair**.

---

## 10. Agent purchase flow — replacement product

```
USER
"Find me the replacement pump for my
Bosch SMS46MI08E in Norway, delivered this week."
        │
        ▼
 ANSWER ENGINE
        │
  discovers/catalog searches
        │
        ▼
   structured merchant candidates
        │
       hard constraint filtering
        │
    ┌───┴───┐
    ▼       ▼
compatibility  stock
    │       │
    └───┬───┘
        ▼
     ranking/trust
        │
        ▼
   OUR PRODUCT
        │
        ▼
    create cart
        │
        ▼
authoritative checkout state
        │
  price / delivery / terms
        │
        ▼
   BUYER CONFIRMS
        │
        ▼
     PAYMENT
        │
        ▼
      ORDER
```

---

## 11. Agent Commerce Compatibility Layer

Take a normal tiny Scandinavian/UK merchant:

```
old Shopify
WooCommerce
CSV inventory
phone bookings
ancient website
```

Turn them into:

```
structured canonical catalog
live price/availability feed
agent-readable service graph
ACP discovery
UCP discovery
MCP
machine-readable policies
canonical entity/part graph
transaction endpoint
agent analytics
```

**Cloudflare for getting selected by agents.**

---

## 12. The highest-value experiment

### Agent Recommendation Laboratory

Take a deliberately obscure Norwegian/Danish/UK test market.

Create controlled merchant variants:

```
A = basic page
B = exhaustive structured specifications
C = B + live inventory
D = C + stronger third-party corroboration
E = D + better returns
F = E + ACP/UCP/MCP/feed
G = F + faster/local delivery
```

Then repeatedly query ChatGPT, Gemini, Claude, Perplexity using realistic intents:

```
"Which replacement part fits X?"
"Buy me X under NOK 1500"
"Find one delivered to Bergen tomorrow"
"Find a reliable Norwegian seller"
"Book someone to install X in Nottingham"
```

Capture:

```
retrieved domains
cited domains
recommended products
merchant chosen
ranking/order
reason stated
price
confidence
transaction ability
```

Then mutate one variable.

**Reverse-engineer the commerce choice function empirically.**

---

## 13. The three biggest discoveries

1. **Local physical services are already being modeled as agent-compatible commerce.** UCP explicitly treats appointment-based services as orderable items and now has serviceability-aware Location search.

2. **Structured feeds/freshness/provenance are emerging as the native information layer between merchants and purchasing agents.** ACP has already merged Product Feeds.

3. **The ecosystem is already designing telemetry for precisely the things we want to measure:** referrals, retrieved/cited content, price provenance, competition and buyer failure reasons.

---

## The GitGoblin Method

Don't scrape "popular GitHub repos." Continuously construct:

```
PROTOCOL
   ↓
PR
   ↓
AUTHOR
   ↓
REVIEWERS
   ↓
REFERENCED ISSUE
   ↓
REFERENCED PR
   ↓
COMPANY
   ↓
OTHER REPOS
   ↓
OTHER MAINTAINERS
   ↓
NEW CAPABILITY
```

Score events heavily when:

```
Google + Shopify agree on primitive
Meta independently implements same primitive
OpenAI ACP adds equivalent
Stripe/payment provider implements downstream piece
W3C discussion references it
independent implementation appears
```

That is a **CAPABILITY_EMERGED** event, not just "new repo found."

---

**GitHub is probably the best alpha source we've found yet for agent commerce.**

Not because GitHub predicts what might happen. Because we're reading the engineers at Google, Shopify, OpenAI/Stripe ecosystem, Meta, Etsy, Target and others **turning it into interfaces before most ecommerce operators realize the interfaces exist**.

---

*Document saved word for word from research session.*
