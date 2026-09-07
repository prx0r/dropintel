# Goblin Alpha 2 — The Implementation Layer

**Date:** 2026-09-07
**Status:** VALIDATED — Enough public code to build intelligence system around agent-commerce stack

---

## Executive Summary

There is now enough public implementation code to build **GitGoblin as an intelligence system around the emerging agent-commerce stack**, rather than just monitoring interesting repositories.

The biggest new finds: **Shopify/shop-chat-agent**, **LiveKit's full phone-booking example**, **Hearthline**, **Arenza's readiness scorer**, **Bolna**, **Lucid Agents**, and the newly expanded **UCP Location/serviceability schema**.

---

## Important Correction: Shopify Discovery Claims

Your two-layer model is correct as an abstraction:

```
SHOPIFY CATALOG
candidate generation / eligibility / ranking
              ↓
EXTERNAL AGENT
intent-specific re-ranking and choice
```

But I would **not yet write these as proven Shopify ranking factors**:

- description completeness
- image coverage
- review depth
- variant completeness
- policy completeness

Those are excellent **agent-readiness features**, and Arenza actually scores them, but we have not found evidence that Shopify uses exactly those five as an internal Catalog ranking formula.

**JSON-LD is absolutely worth doing, but Shopify Catalog primarily has privileged access to Shopify's structured merchant/catalog data. PDP JSON-LD is more important for Google, crawlers and non-Shopify agents.**

Schema.org already has:

- `isAccessoryOrSparePartFor`
- `isConsumableFor`

for explicit Product→Product compatibility edges. That belongs in `drop` immediately.

---

## GitGoblin S-tier: Clone These First

| Repository | Why S-tier | What to Extract |
|------------|------------|-----------------|
| **Shopify/ucp-cli** | Public instructions telling agents how to shop Shopify | query rewriting, context fields, hard filters, seller fields, schema changes |
| **Universal-Commerce-Protocol/ucp** | The actual future commerce/service grammar | schemas, capabilities, Location, serviceability, constraints |
| **Shopify/shop-chat-agent** | Shopify's own storefront shopping-agent implementation | MCP tools, auth boundary, prompt, cart/order flow |
| **Shopify/claude-for-commerce-examples** | Anthropic agents connected to real Shopify | real backend adapters, staged merchant writes |
| **anthropics/commerce-agents** | Best readable commerce-agent reference architecture | ranking, tools, gates, prompts, evals |
| **gil--/ucp-agent-imessage** | Real-merchant shopping agent with purchase state machine | provenance, authorization, carts, buyer identity, payment |
| **NVIDIA-AI-Blueprints/Retail-Agentic-Commerce** | Full open ACP/UCP search/recommendation/promotion stack | actual ranking thresholds and agent configs |
| **arenza-ai/agentic-commerce-score** | Direct competitor to our Agent Recommendation Lab | readiness features, deterministic scoring |
| **codewithmuh/hearthline** | Closest open implementation of our free Supplier OS wedge | lead capture, quoting, booking, CRM, call state |
| **livekit/agents** | Serious open realtime voice runtime | turn detection, tools, telephony, handoffs |
| **livekit-examples/python-agents-examples** | Production patterns rather than framework abstractions | receptionist, observers, payments, multi-agent booking |
| **livekit/sip** | Telephony primitive beneath a self-owned receptionist | SIP lifecycle and routing |
| **pipecat-ai/pipecat** | Alternative fully controlled voice pipeline | frames, STT/LLM/TTS orchestration, interruption |
| **bolna-ai/bolna** | Entire open hosted-style voice-agent backend | provider abstraction, WebSockets, telephony, Redis |
| **TimefoldAI/timefold-solver** | Probook-like optimization brain primitive | constraint solving, objective architecture |
| **TimefoldAI/timefold-quickstarts** | Readable routing/field-service examples | visits, availability, travel, skills |
| **Accio-org/BusinessArena** | Autonomous ecommerce operator benchmark | strategies, capital allocation, trajectories |
| **Accio-org/CommerceAgentBench** | Long-horizon commerce task/eval corpus | workflows, verifiers, failure modes |
| **vercel/acp-handler** | Very clean merchant-side ACP transaction adapter | idempotency, signatures, payment state |
| **agentcommercekit/ack** | Agent identity/trust/payment receipts | DID, credentials, KYA, receipts |
| **daydreamsai/lucid-agents** | Machine-commerce service runtime | discovery, schemas, payment admission, tasks |
| **paypal/agent-toolkit** | Production financial tools designed for agents | invoices, refunds, subscriptions, disputes |
| **stripe/ai** | Stripe's agent/tool infrastructure | payment agent surfaces |
| **openreferral/specification** | Years of prior art for structured service directories | organisation/service/location graph model |
| **TEN-framework/ten-framework** | Third independent open realtime voice architecture | VAD, turn detection, SIP, chained vs realtime |

---

## The New Shopify Seed: Shopify/shop-chat-agent

Shopify's official reference storefront AI assistant. Supports:

```
natural-language catalog discovery
policy / FAQ search
cart creation + mutation
checkout initiation
order lookup
returns
```

Architecture connects to **two separate MCP servers**:

```
STOREFRONT MCP
product/catalog/cart
anonymous-ish commerce state

CUSTOMER MCP
orders/customer information
authenticated customer state
```

The code dynamically does `tools/list`, translates those tool schemas for the model, and dispatches a proposed invocation to the appropriate server. A 401 from customer MCP triggers authorization.

**Reusable Supplier OS principle:**

```
PUBLIC SUPPLIER CAPABILITIES
         ≠
CUSTOMER-SPECIFIC STATE
         ≠
PRIVILEGED MUTATIONS
```

Do not hand one enormous omnipotent tool collection to the model.

---

## UCP Location Is Much Bigger Than I Thought

The actual official schema now describes Location Search as supporting:

```
natural-language query
distance relation
serviceability relation
structured filters
current item availability
pagination
```

And crucially:

> `distance`, `serves` and supplied filters combine with **AND**; the natural-language query cannot relax them.

`serves` can express either:

```
point:
  latitude
  longitude

address:
  country
  region
  postal_code
```

And if the business cannot authoritatively evaluate the service target, the spec says it should **reject**, rather than silently broadening the result.

Location filters additionally include:

```
open_at
amenities
current item availability
```

And every requested item must currently be available at that candidate location.

**Translate that to EV installation:**

```
query:
  "install 7kW home charger"

serves:
  address:
    postal_code: NG7 ...

filters:
  open_at: requested survey time

extensions:
  dev.drop.services:
      oz_ev_approved: true
      phase: single_phase
      charger_brands: [...]
      max_distance_km: ...
      installation_types: [...]
      survey_available: true
```

**We should model our Service Graph as a superset of UCP Location, not invent a completely bespoke representation.**

---

## Closest Open Competitor: Hearthline

`codewithmuh/hearthline` — explicit open-source AI front desk for home-service businesses.

Architecture:

```
Voice
SMS
WhatsApp
Email
Web chat
      ↓
AI receptionist
      ↓
qualify lead
check availability
draft quote
book appointment
      ↓
customer / lead / quote / job records
```

Stack:

```
Next.js
Django / DRF
Postgres

Vapi
  ↓
STT → LLM → TTS

Twilio
Claude/OpenAI
```

**Its bugs are more valuable than its architecture.**

Vapi calls the model repeatedly without replaying all previous tool history, so Hearthline added application-level dedupe around:

```
qualify_lead
draft_quote
book_appointment
check_availability
```

And caches tool results per call. Also treats telephony-verified caller number as authoritative rather than trusting LLM-extracted phone number.

**A commit adding a dedupe cache is more valuable than a founder tweeting "voice AI is the future."**

---

## The LiveKit Example Is Nearly a Supplier OS Prototype

Doheny Surf Desk Booking Agent — phone receptionist architecture.

Five specialized agents:

```
FrontDeskAgent
     ↓
IntakeAgent
     ↓
SchedulerAgent
     ↓
GearAgent
     ↓
BillingAgent
```

Plus **parallel ObserverAgent** that periodically watches conversation and checks:

```
safety
injuries
customer profile inconsistencies
skill mismatch
special handling
```

Then injects context/guardrails back into active receptionist.

**For EV installation:**

```
FAST VOICE AGENT
talk naturally
capture intent
answer questions

       +

SLOW OBSERVER
continuously derive:
- property type
- homeowner/tenant
- parking situation
- fuse board
- likely DNO requirement
- grant eligibility
- safety issue
- confidence
- missing qualification field

       ↓

inject:
"Before booking, ask about off-street parking."
```

The customer never experiences a cumbersome questionnaire. The graph forms **passively during conversation**.

---

## Voice Stack: Four Levels

| Layer | Projects | Use |
|-------|----------|-----|
| Managed orchestration | Vapi, Retell | Fastest MVP |
| Application-owned realtime | **LiveKit Agents** | Best balance for us |
| Fully composable pipelines | **Pipecat**, **Bolna**, TEN | Maximum control |
| Native speech-to-speech | OpenAI Realtime etc. | Lowest-complexity audio reasoning |

**For prototype:**

```
LiveKit + Twilio/Telnyx SIP + Deepgram + cheap fast LLM + Cartesia/Deepgram TTS
Postgres + durable deterministic tool service
```

**Hearthline gives us the business workflow. LiveKit gives us the infrastructure architecture.**

---

## Closed Competitors: Intelligence Targets, Not Clone Targets

No meaningful public backend found for: **Probook, Avoca, Sameday**.

Mine instead:

```
employee GitHubs
PR activity outside company org
job descriptions
engineering blogs
dependencies accidentally revealed in docs
conference talks
open-source contributions
SDK integrations
former employees
founders' X follow/reply graphs
```

**Avoca stack leak:** TypeScript/JavaScript, Next.js, React, Node/Fastify, PostgreSQL, AWS

**Probook scale claims:** 58,000+ customer interactions daily, 90% dispatch automated across 220+ techs

---

## The Emerging Picks-and-Shovels Map

### 1. Agent-readiness / visibility

Arenza's territory. Open scorer measures discoverability, evaluateability, transactability.

**Our improvement:** Vertical-specific scoring. "An agent looking for a Bosch SMS46MI08E cannot conclusively establish that SKU 00631200 fits it."

### 2. Agent Recommendation Observatory

Run canonical buyer intents against Shopify Catalog, ChatGPT, Gemini, Copilot, Google AI Mode.

Store: query, candidate set, rank, chosen product, seller, price, reason, timestamp, agent/model.

Perturb listing fields experimentally.

### 3. Agent-native service directory

UCP Location + our extensions.

### 4. Supplier front desk

Hearthline + LiveKit architecture. Free initially.

### 5. Dispatch optimizer

Timefold + learned historical outcome models.

```
LLM extracts job requirements
        ↓
constraint solver generates feasible matches
        ↓
predictive model estimates outcomes
        ↓
optimizer assigns
```

### 6. Transaction gateway

`vercel/acp-handler` — idempotency, request signatures, session state, two-stage payment.

### 7. Agent payments / procurement

`daydreamsai/lucid-agents` — typed services with discovery, policy, idempotency, fulfillment, payments.

### 8. Financial action toolkit

`paypal/agent-toolkit` — invoices, payments, refunds, disputes, shipment tracking, subscriptions.

---

## GitGoblin Should Stop Being Repo-Monitoring Software

New data model:

```
PERSON
  ├─ X account
  ├─ GitHub account
  ├─ employer
  ├─ previous employers
  ├─ repos contributed to
  ├─ PR reviewers
  └─ social interactions

REPOSITORY
  ├─ organization
  ├─ domain
  ├─ architecture
  ├─ algorithms
  ├─ schemas
  ├─ prompts
  ├─ tools
  ├─ tests
  └─ dependencies

CONCEPT
  ├─ catalog ranking
  ├─ serviceability
  ├─ dispatch
  ├─ voice turn detection
  ├─ payment authorization
  ├─ identity
  ├─ recommendation
  └─ attribution

CHANGE
  ├─ person
  ├─ repo
  ├─ file/path
  ├─ concept
  ├─ semantic diff
  └─ importance
```

Detect relationships a normal GitHub watcher misses:

```
gil-- modifies Shopify/ucp-cli
       ↓
change adds ranking signal
       ↓
same concept appears in UCP schema PR
       ↓
new Shopify documentation appears
       ↓
three independent signals =
HIGH CONFIDENCE PLATFORM CHANGE
```

---

## Event Detectors to Implement

```text
ALGO_SURFACE_CHANGED
ranking, score, weight, threshold, filter, sort, relevance, similarity, rerank

DISCOVERY_SURFACE_CHANGED
catalog, search, lookup, query, context, intent, taxonomy, identifier, metadata

SERVICE_GRAPH_CHANGED
location, serves, distance, availability, hours, skills, certification, service_area

TRANSACTION_SURFACE_CHANGED
cart, checkout, order, payment, authorization, capture, refund, idempotency

VOICE_SURFACE_CHANGED
vad, turn_detector, interruption, barge_in, sip, handoff, transfer, latency, tool_call

SUPPLIER_OS_CHANGED
lead, qualification, quote, booking, scheduler, dispatch, technician, crm, fsm

TRUST_SURFACE_CHANGED
identity, credential, provenance, rating, review, reputation, fraud

AGENT_POLICY_CHANGED
prompt, SKILL.md, tool description, guard, policy, approval, permission

EVAL_SURFACE_CHANGED
benchmark, judge, fixture, trajectory, score, pass, simulation
```

Upweight changes inside:

```
**/schemas/**
**/skills/**
**/prompts/**
**/tools/**
**/agents/**
**/solver/**
**/search/**
**/ranking/**
**/recommendation/**
**/checkout/**
**/payments/**
**/tests/**
**/eval/**
```

---

## People/Clusters to Monitor

**Shopify/UCP:** Ilya Grigorik, Gil Greenberg, Catalog/Location/request-constraints contributors

**Anthropic commerce:** Ali Shazal, Matthew Koen, commerce-agents contributors

**Voice infrastructure:** LiveKit core, Daily/Pipecat, Bolna, TEN (@elliotchen200, cyfyifanchen)

**Optimization:** Geoffrey De Smet, Radovan Synek, Lukáš Petrovický, Timefold field-service mergers

**Vertical AI:** Lewis Zhang (Probook), Tyson Chen/Apurva Shrivastava (Avoca), senior AI/FDE hires

**Evaluation/visibility:** Arenza, MentionNetwork, agent-commerce readiness tooling

**Machine commerce:** Lucid/Daydreams, ACK/Catena, x402, ACP, UCP, PayPal/Stripe agent-tool teams

---

## What to Build Tomorrow

```text
gitgoblin/corpus/
    commerce/
    service-discovery/
    voice/
    dispatch/
    payments/
    evals/
    visibility/
```

Clone S-tier set. Build daily extraction producing:

```json
{
  "repo": "Shopify/ucp-cli",
  "commit": "...",
  "concepts": ["catalog_search", "ranking"],
  "algorithmic_surfaces": [],
  "schemas": [],
  "tools": [],
  "prompts": [],
  "constraints": [],
  "numeric_constants": [],
  "external_services": [],
  "people": [],
  "semantic_changes": [],
  "drop_implications": []
}
```

Build **cross-repo concept pages**:

```
/concepts/serviceability

UCP: serves + distance + filters
Timefold: travel + time window + skills
Probook: service location + tech history + ETA
Hearthline: business availability + booking
OpenReferral: service + organization + location
```

**Five separate ecosystems converging on the same primitive = the alpha.**

---

## The Single Strongest New Strategic Conclusion

> **The opportunity isn't "GEO for commerce." It is building the missing stateful compatibility + serviceability + availability graph between intent and transaction.**

Products need:

```
WHAT IS THIS?
WHAT DOES IT FIT?
CAN I GET IT?
FROM WHOM?
AT WHAT PRICE?
WHEN?
CAN I TRANSACT?
```

Services need:

```
WHAT DO YOU DO?
CAN YOU DO THIS EXACT JOB?
DO YOU SERVE THIS LOCATION?
ARE YOU QUALIFIED?
WHEN CAN YOU COME?
WHAT WILL IT COST?
CAN I BOOK?
```

**The front desk is simply how we keep that service graph current.**

**The Shopify store is simply how we monetize the product graph.**

---

## Next Rabbit Hole

Crawl every contributor/reviewer on UCP `Location`, Catalog and request-constraints changes, every contributor to Shopify's agent repos, and every maintainer of Hearthline/LiveKit booking flows, then pivot through their personal repos and X graphs.

**That's where the next genuinely hidden projects will appear.**

---

*Document saved word for word from research session.*
