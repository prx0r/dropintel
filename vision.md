# Vision — The Complete Thesis

**Date:** 2026-09-07
**Status:** VALIDATED — Eleven business models, one unified architecture

---

## The One Sentence

> **We are not building voice agents or dropshipping stores. We are building adapters that turn messy real-world suppliers into reliable, transactable endpoints for AI agents.**

---

## What Is Already Commoditizing

**Voice itself is largely solved enough.** Retell is pay-as-you-go at $0.07–$0.31/min. ServiceTitan has Voice Agent booking. Housecall Pro has CSR AI.

**Do not spend months inventing STT, TTS, VAD or a generic AI receptionist.**

Use LiveKit/Retell/Vapi initially. Own the layer above it.

---

## The Unsolved Problem

```
MESSY SUPPLIER
phone
WhatsApp
PDF price list
ancient website
calendar in his head
supplier catalog
certificates in email
        ↓
OUR ADAPTER
        ↓
structured capabilities
live availability
normalized prices
verified credentials
exact compatibility
transaction state
        ↓
ANY AGENT
ChatGPT / Gemini / website / voice / API
```

**That is the company.**

---

## Eleven Business Models

### 1. Free Supplier Front Desk → Service Fulfillment Network

```
"Forward your missed calls to this number.
It answers, qualifies the job, sends everything to your WhatsApp
and can book work into free slots. Free trial."
```

WhatsApp is the primary operator interface for UK trades.

**The tradesman's experience:**

```
Incoming WhatsApp:

NEW LEAD
EV charger installation
NG7 2AB
Homeowner: yes
Off-street parking: yes
Supply: single phase
Preferred: Thursday afternoon

Likely standard install
Estimated range: £850–£1,050

[Accept]
[Suggest time]
[Call customer]
[Decline]
```

He hits **Accept**. Customer gets confirmation.

Behind that simple interaction, we acquire:

```
service_area
acceptance behaviour
actual availability
price
job types accepted
equipment supported
response time
conversion
completion
cancellations
actual invoice
duration
travel time
customer satisfaction
```

**That's the graph.**

---

### 2. Compatibility Dropshipping

```
USER
📸 photo of broken component

"Where can I get another one?"

        ↓

AGENT
identifies appliance
identifies component candidates
reads model / serial evidence
checks compatibility graph
checks supersessions

        ↓

"Yes — this is Bosch part 00631200.
It fits SMS46MI08E.
£71.40 delivered tomorrow."

        ↓

BUY
```

**The margin is compensation for solving information entropy.**

The supplier may already have warehouse, purchasing relationships, stock, packing, courier contracts.

They're terrible at: titles, images, structured compatibility, GTIN/MPN normalization, model mappings, supersessions, product discovery, customer support, machine-readable stock, agentic checkout.

**We fix the bad half.**

---

### 3. Photo → Purchase Order for Tradesmen

B2B version. Electrician sends:

```
📸 [photo]

"Need two of these tomorrow morning near Derby."
```

System:

```
identify part
  ↓
confirm electrical characteristics
  ↓
find compatible alternatives
  ↓
query Screwfix / wholesalers / independents / distributors
  ↓
compare: price, stock, distance, delivery, trade discount
  ↓
"2 × Hager ___
CEF Derby has stock.
£42.80 ex VAT.
Collect 07:30 tomorrow."

[ORDER]
```

**Every procurement interaction improves our parts graph.**

---

### 4. Agentic RFQ Broker

Customer says: "I need a 7kW charger installed at this house."

We construct one standardized job object and contact qualified suppliers:

```
Jim → WhatsApp
Sarah → API
ABC Electrical → email
Dave → automated phone call
```

Turn every response into structured offers. Customer receives **three actually executable offers**, not three phone numbers.

**Commission on outcome, not leads.**

---

### 5. "API Virtualization" for Analogue Businesses

We don't need the plumber to have an API. **We become his API.**

```
check_availability(
  supplier="JimElectrical",
  job="EV_INSTALL_STANDARD",
  postcode="NG7",
  date="2026-09-10"
)

Our backend knows Jim has no API.

Internally:
cache/calendar says maybe
       ↓
WhatsApp Jim:
"Can you take NG7 EV install Thurs afternoon?"
       ↓
Jim: 👍
       ↓
structured response returned
```

**Human WhatsApp is just a slow backend adapter.**

---

### 6. Service SKUs

Physical products have SKUs. Trades mostly don't. Agents need them.

```
EV-INSTALL-7KW-STANDARD
EV-INSTALL-7KW-LONG-RUN
EV-INSTALL-LOAD-MANAGEMENT
EV-INSTALL-3PHASE
EV-INSTALL-SURVEY

BOILER-SERVICE-COMBINATION
BOILER-PUMP-REPLACE
FUSEBOARD-10WAY-RCBO
```

Each has: qualification fields, required certification, expected duration, parts, normal price range, exclusions, warranty, evidence required.

**This is how services become agent-readable.**

---

### 7. Compatibility Graph as an API

```
POST /resolve

{
  "manufacturer": "Bosch",
  "model": "SMS46MI08E",
  "component": "circulation pump"
}

→ OEM: 00631200
→ supersedes: 00651956
→ compatible: [SMS46MI08E, SMS50MI08E, ...]
→ confidence: 0.997
```

Sell to: retailers, agents, repair companies, insurers, marketplaces, manufacturers, call centers.

**Picks-and-shovels company.**

---

### 8. Agentic Aftersales-as-a-Service

Tell mid-sized manufacturers:

> Give us your PDFs, spreadsheets, distributor lists and spare-part files.

We return: normalized product graph, compatibility graph, Shopify storefront, Catalog-ready data, MCP endpoint, AI parts assistant, photo lookup, checkout, returns, analytics.

**Revenue: setup fee + monthly fee + transaction %.**

---

### 9. The Installed-Base Graph

Every transaction tells us a household owns something.

```
HOUSEHOLD
├── Bosch SMS46MI08E
│   ├── bought: ...
│   ├── pump replaced: 2026
│   └── expected maintenance: ...
├── Zappi v2 charger
│   ├── installed by Jim
│   ├── warranty until ...
│   └── installation certificate
├── Vaillant boiler
└── Tesla Model 3
```

**Household infrastructure memory. Recurring demand.**

---

### 10. Supplier Trust Graph

Empirical outcomes, not star ratings:

```
quoted £950
actually invoiced £975

promised Thursday
arrived Thursday

estimated 3h
took 2h47

187 booked
181 completed
3 cancelled supplier-side
3 customer-side

6 disputes
5 resolved
```

**Machine-useful trust.**

---

### 11. Grants / Compliance / Financing

EV is constrained by rules. After qualification:

```
customer eligible?
property eligible?
installer certification?
charger eligible?
grant?
DNO notification?
building requirements?
```

Agent handles paperwork. Then: solar → battery → heat pump → insulation.

**Home electrification transaction. Financing becomes obvious.**

---

## The Unified Architecture

```
                   USER INTENT
                       │
           ┌───────────┴────────────┐
           ▼                        ▼
       PRODUCT                  SERVICE
    "need this pump"         "install charger"
           │                        │
           ▼                        ▼
    IDENTIFICATION             QUALIFICATION
           │                        │
           ▼                        ▼
 COMPATIBILITY GRAPH          SERVICE SKU
           │                        │
           └───────────┬────────────┘
                       ▼
                SUPPLIER GRAPH
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
       API/feed     WhatsApp      phone
       supplier     supplier      supplier
           │           │           │
           └───────────┼───────────┘
                       ▼
                  NORMALIZER
                       ▼
            price / availability /
          trust / compatibility / ETA
                       ▼
                 TRANSACTION
                       ▼
           payment / booking / PO
                       ▼
                  FULFILLMENT
                       ▼
             OBSERVED OUTCOME
                       │
                       └──────────────┐
                                      ▼
                                  THE GRAPH
```

**One system. Not two codebases.**

---

## What NOT to Build

- ❌ New TTS engine
- ❌ Generic voice-agent infrastructure
- ❌ Another generic trades CRM
- ❌ Another Thumbtack/Checkatrade directory
- ❌ Generic visual product search
- ❌ Generic chatbot builder
- ❌ Another Shopify theme
- ❌ Enormous contractor dashboard

**All have serious incumbents. Integrate or sit above them.**

---

## Two Ridiculously Clean Experiments

### Experiment A: One Trade, One City

**EV charger installers, Nottingham.**

Build: phone forwarding, WhatsApp operator interface, lead qualification, service-area rules, certification fields, availability, quote generation, slot hold, booking, job completion.

Onboard **10 electricians for free**.

Their dashboard is WhatsApp.

Measure: calls handled, qualified leads, booking rate, time to confirmation, accepted jobs, actual price, completion rate, human interventions/job.

### Experiment B: One Replacement-Parts Vertical

Choose something with disgusting compatibility complexity:

```
appliance spare parts
boiler/HVAC parts
coffee-machine parts
power-tool parts
commercial kitchen equipment
garden machinery
```

Build only: photo/model intake → exact part resolver → compatibility evidence → 3 supplier feeds → normalized Shopify SKU → agent-friendly PDP → checkout.

100–500 products is enough.

Test: **higher certainty beats Amazon/generalist merchants.**

---

## The Convergence

Someone asks: "My dishwasher isn't draining."

We identify the pump.

```
Would you like:

A. Pump only — £68, tomorrow
B. Pump + installation — £149, Wednesday 10–12
```

**Product graph + service graph.**

Or: "My Zappi isn't charging."

```
Likely CT clamp fault.

A. Replacement CT clamp — £29
B. Certified technician diagnostic — £89 tomorrow
```

---

## The Deepest Moat

> **For a real-world problem, what exact product/service combination will fix it, who can fulfill it, when, at what price, and with what probability of success?**

**That graph does not currently exist.**

---

## Revenue Models

| Model | Revenue | Timeline |
|-------|---------|----------|
| Supplier OS | Booking fee + subscription | Month 1 |
| Compatibility Dropshipping | Product margin | Month 2 |
| Agent Commerce Audit | One-time + monthly | Month 2 |
| Service Marketplace | Booking commission | Month 3 |
| Compatibility API | Data licensing | Month 4 |
| Aftersales-as-a-Service | Setup + monthly + % | Month 6 |
| Installed-Base Graph | Recurring demand | Month 6+ |
| Financing | Underwriting margin | Month 9+ |

---

*Document saved: 2026-09-07*
