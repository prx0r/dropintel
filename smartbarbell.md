# Smart Barbell — The Resolution Broker Thesis

**Date:** 2026-09-07
**Status:** VALIDATED — Three core businesses, one unified graph

---

## The Missing Jump

> **Stop thinking "products to dropship." Build the best machine-readable index of boring things that already exist, break, wear out, become obsolete, or need servicing.**

Then let agents bring the demand.

---

## The Two Wedges Are Really One Business

```
                     REAL-WORLD PROBLEM
                            │
                  photo / model / symptom
                            │
                            ▼
                    RESOLUTION ENGINE
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
        NEEDS A THING                  NEEDS A HUMAN
             │                             │
             ▼                             ▼
      PRODUCT GRAPH                  SERVICE GRAPH
             │                             │
      supplier router                 bid router
             │                             │
             ▼                             ▼
    cheapest valid source          contractor accepts
             │                             │
             ▼                             ▼
        BUY / AFFILIATE               LEAD UNLOCK
```

**You aren't really a dropshipper. You aren't really Checkatrade. You're a resolution broker.**

---

## Three Core Businesses

### A. Agentic Job Broker

```
problem
→ structured job
→ supplier bids
→ selected contractor pays lead unlock fee
```

**No commission. No bullshit.**

Pay £20/£40/£70 only when you actively choose to unlock a qualified job.

### B. Agentic Replacement Broker

```
photo/problem
→ exact identity
→ compatibility
→ best geographically appropriate seller
→ margin / affiliate / dropship
```

### C. Supplier Normalization Network

```
messy suppliers
→ inventory
→ pricing
→ availability
→ capabilities
→ normalized API
```

**C feeds both A and B.**

---

## The Contractor Model (Simplified)

```
CUSTOMER
"I need a Zappi installed Thursday in NG7"
        ↓
we qualify it properly
        ↓
broadcast anonymized job
        ↓
8 suitable installers receive:

NG7
standard Zappi installation
Thursday afternoon
off-street parking
11m cable run
customer ready to book

Can you do it?

[YES £X]
[NO]
        ↓
installer bids / accepts
        ↓
customer selects
        ↓
INSTALLER PAYS £X LEAD FEE
        ↓
both parties get details
        ↓
WE ARE DONE
```

**No subscription. No commission. Pay only when you actively choose to unlock a qualified job.**

---

## The Free Receptionist Feeds the Broker

Initially we know:

```
Jim:
EV installer
Nottingham
OZEV
```

After three months of his free receptionist:

```
Jim:
NG1-NG15
Zappi / Ohme / Wallbox
standard install £850–£975
long runs +£X/m
single phase yes
three phase yes
Thursday generally free
responds in 3m
accepts 41% of Zappi jobs
rejects flats
actual completion 96%
```

**Every phone call makes our broker better. Voice is the data collection mechanism. Not the product.**

---

## The "Broken Things Index"

Don't organize the catalog like Amazon. Build a graph around what users tell agents:

```
"this broke"
"what is this?"
"where do I buy another?"
"this display says E14"
"I lost this remote"
"what filter fits this?"
"this plastic connector cracked"
"what is the new version of this?"
```

Agent workflow:

```
PHOTO
  ↓
visual fingerprint
  ↓
brand
  ↓
model family
  ↓
generation
  ↓
component
  ↓
part number
  ↓
supersession
  ↓
compatibility
  ↓
local supply
```

---

## Visual Compatibility Graph

For each object, collect:

```
PRODUCT: Bosch 00631200

visual evidence:
    front, back, top, connector, mounting points
    label/data plate, packaging
    installed appearance, old/discolored appearance

identifiers:
    OEM, EAN/GTIN, manufacturer SKU
    aliases, old SKUs, replacement SKUs

physical:
    dimensions, voltage, connectors, mounting geometry

compatibility:
    model A, model B, model C

incompatibility:
    looks similar but DOES NOT fit model D

location:
    Norway suppliers, Finland suppliers, Sweden suppliers

commercial:
    landed cost, stock, ETA, returns
```

**The particularly valuable data is: "Looks almost identical, but this is NOT the one."**

---

## Hard Niches (Not Generic)

### `hyttepumpe.no`
Everything weird that breaks around Norwegian cabins.

### `ilmalampopumppu-varaosat.fi`
Exact-model lifecycle components for Finnish air-to-air heat pumps.

### Weather-station lifecycle specialist
Davis generations, transmitters, consoles, sensors, supersessions.

### Sauna control replacement
Old controller/photo → identify → current compatible successor.

### Robot-mower lifecycle
```
mower photo → model/year → blade, battery, wheel, charging station,
boundary-wire component, power supply, replacement machine
```

### Cabin water/frost systems
A Norwegian cabin is basically an **installed-base graph of obscure components sitting unattended in brutal weather**.

---

## Supersession Commerce

Objects live longer than SKUs:

```
OLD PART: ABC-001
   ↓ discontinued
ABC-002
   ↓ superseded
ABC-003
   ↓ regional variant
ABC-003-EU
```

Build:

```
part: ABC-001
valid_from: 2009
valid_to: 2014
superseded_by: ABC-002
supersession_type: exact / requires_adapter / partial
incompatible_for_models: [...]
```

**That's a real asset.**

---

## Local-Language Alias Graph

One object described as:

```
OEM English term
manufacturer internal name
Norwegian trade name
Norwegian colloquial name
Finnish technical term
Finnish colloquial term
Swedish trade term
common misselling
part number
old part number
```

Now: terrible Finnish description + terrible photo → correct global entity.

**GeoDrop's linguistic moat.**

---

## Market-Selection Formula

```
AGENTIC_REPLACEMENT_SCORE =

installed_base
× failure_frequency
× identification_difficulty
× compatibility_complexity
× supplier_fragmentation
× local_language_fragmentation
× gross_margin
× shipping_suitability
× image_identifiability
× urgency

÷
amazon_quality
÷ manufacturer_DTC_quality
÷ return_risk
```

---

## The Monster Long-Term Graph

```
                  PHOTO / PROBLEM
                        │
                        ▼
                    ASSET ID
                        │
                  what exactly is it?
                        │
                        ▼
                  FAILURE STATE
                        │
              what does it actually need?
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
          PART                    LABOUR
            │                       │
            ▼                       ▼
  COMPATIBILITY GRAPH          SERVICE SKU
            │                       │
            ▼                       ▼
    SUPPLIER INVENTORY       CONTRACTOR GRAPH
            │                       │
            └───────────┬───────────┘
                        ▼
                  GEO ROUTER
                        │
          cheapest / fastest / safest
                        │
                        ▼
                     SOLVED
                        │
                        ▼
                 OUTCOME CAPTURE
                        │
                        ▼
                  BETTER GRAPH
```

---

## The Real Target

> **Every boring physical object whose owner will eventually point a camera at it and ask an AI: "what the hell is this, and how do I fix/replace it?"**

That is an enormous search surface. Unlike generic ecommerce, most of it is currently served by old distributors, PDFs, local wholesalers and terrible websites.

**That is GeoDrop 2.0.**

---

*Document saved: 2026-09-07*
