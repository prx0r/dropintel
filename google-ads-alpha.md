# Google Ads Alpha — The Engineers Behind AI Max

**Date:** 2026-09-07
**Status:** VALIDATED — Key people identified

---

## The Breakthrough

Google Merchant Center now has **conversational product attributes specifically for AI Mode**.

These include:

```
product_detail          — 100 structured technical specs
question_and_answer     — 30 Q&As for AI to quote
related_product         — required_part, substitute, accessory
document_link           — manuals, guides, PDFs
item_group_title        — variant grouping
variant_option          — variant-specific properties
popularity_rank         — relative popularity score
```

**Google explicitly says `related_product` supports spare parts and substitutes.**

**Google explicitly says `product_detail` is for AI Mode.**

---

## Key People to Track

### Max George — The Ghost

```
Former Google Agentic Commerce Lead
Now: Yale Guest Lecturer

Built: UCP, Shopping in AI Mode, Shopping in Gemini,
       Agentic Checkout, Business Agent

Left Google April 2026.
```

**She built the entire stack. Now she's teaching it.**

Her LinkedIn posts are pure alpha.

### Vivek Chandran — The Current Lead

```
TPM Lead, AI Overview & Mode
Google Shopping

"Orchestrating complex initiatives at the intersection of
Core Search and Generative AI for billions of users daily."

Currently: AI Overview and AI Mode in Shopping
```

**He's the person to watch.**

### Brandon Ervin — AI Max

```
Director of Product Management, Google Ads

Launched AI Max for Shopping campaigns.
"The feed is a deep product database, not a static list."
```

### Emmanuel Flossie — The Identifier

```
FeedArmy founder
Google Ads Diamond Product Expert

Identified the 8 conversational attributes.
Published canonical video guide May 24, 2026.
```

---

## The Feed Strategy

For each product, submit:

```
STANDARD FIELDS
id, title, description, price, availability, brand, mpn, gtin
image_link, additional_image_link
shipping, condition

CONVERSATIONAL ATTRIBUTES
question_and_answer (30 Q&As)
related_product (30 relationships)
product_detail (100 specs)
document_link (5 PDFs)
item_group_title
variant_option
popularity_rank
```

**That's the machine-readable product graph.**

---

## The SEO Advantage

**Yes, this gives us a massive advantage.**

| Competitor | Us |
|------------|-----|
| "pump-123.jpg — pump bosch — £69" | "Bosch 00631200, compatible with SMS46MI08E, 230V, Q&A, manual" |
| Static title | Dynamic title via AI Max |
| No relationships | required_part, substitute, accessory |
| No Q&A | 30 pre-answered questions |
| No documentation | PDFs attached |

**Google literally tells the AI what to recommend. We fill the fields.**

---

## The Priority

1. **question_and_answer** — highest leverage
2. **popularity_rank** — cheap to compute
3. **related_product** — compatibility graph
4. **product_detail** — technical specs
5. **document_link** — manuals
6. **variant_option** — for variant-heavy catalogs

---

*Document saved: 2026-09-07*
