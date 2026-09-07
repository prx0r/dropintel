# Google Merchant Center — The Agent Commerce Layer

**Date:** 2026-09-07
**Status:** VALIDATED — Google built exactly what we need

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

**Google explicitly says `question_and_answer` is for conversational AI.**

---

## The `related_product` Attribute

This is the compatibility graph field.

```
related_product:
    relationship_type: required_part
    identifier_type: id
    identifier: AZ7A

    relationship_type: substitute
    identifier_type: gtin
    identifier: 811571013579

    relationship_type: accessory
    identifier_type: id
    identifier: MILK-FROTHER-PITCHER
```

**Relationship types:**

| Type | Meaning | Example |
|------|---------|---------|
| `required_part` | Needed for function | Battery for lamp |
| `substitute` | Alternative product | Comparable printer |
| `accessory` | Optional add-on | Webcam for computer |
| `often_bought_with` | Frequently purchased together | Phone case with phone |
| `different_brand` | Same product, different brand | Store-brand version |
| `part_of_set` | Part of same product line | Chair for dining set |

**Up to 30 related products per item.**

---

## The `product_detail` Attribute

100 structured technical specs per product.

```
product_detail:
    section_name: Compatibility
    attribute_name: Compatible Model
    attribute_value: SMS46MI08E

    section_name: Electrical
    attribute_name: Voltage
    attribute_value: 230 V

    section_name: Identification
    attribute_name: OEM Part Number
    attribute_value: 00631200
```

**Google says this helps products appear in AI Mode.**

---

## The `question_and_answer` Attribute

30 Q&As for AI to quote directly.

```
question_and_answer:
    "Does Bosch 00631200 fit SMS46MI08E?": "Yes, compatible with SMS46MI08E and SMS50MI08E"
    "Does this replace 00611332?": "Yes, 00631200 supersedes 00611332"
    "Will I need an adapter?": "No, direct replacement"
```

**Google says this is for conversational AI experiences.**

---

## The `document_link` Attribute

Attach manuals and guides.

```
document_link: https://example.com/manual.pdf, https://example.com/assembly.pdf
```

**Up to 5 PDFs, 50MB each.**

---

## AI Max for Shopping (Beta)

Google's new ad system that uses feed data for conversational queries.

**What it does:**

1. **Text customization** — Dynamically rewrites product titles to match shopper intent
2. **Final URL Expansion** — Matches landing pages to query intent
3. **Optimal Format Selection** — Chooses text vs Shopping ad automatically

**Key insight:**

> Google AI treats your GMC feed as a **deep product database** rather than a static list. It extracts key product attributes to match complex, long-tail queries with high precision.

**So our feed becomes the source for:**

```
Shopify Catalog → ChatGPT
Merchant Center → Google AI Mode
Merchant Center → Google Lens
Merchant Center → Shopping Ads
```

---

## The Complete Feed Strategy

For each product, we submit:

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

## The Funnel

```
USER HAS PHYSICAL THING
          ↓
    takes photograph
          ↓
┌─────────┴─────────┐
▼                   ▼
ChatGPT          Google Lens
▼                   ▼
vision             Shopping Graph
▼                   ▼
intent             Merchant Center
▼                   ▼
shopping        AI Mode
retrieval           │
│                   │
├── Shopify Catalog │
├── ACP             │
├── web             │
│                   │
└─────────┬─────────┘
          ▼
     PRODUCT ENTITY
          │
          ▼
    MERCHANT CHOICE
          │
          ▼
        OURS
```

---

## Why This Changes Everything

**Before:** "Make your Shopify listing better for AI."

**After:** "Google literally built the fields for compatibility graphs, spare parts, and technical specs. We fill them."

**The infrastructure is built. We just need to supply the data.**

---

## The Niche

Not "spare parts store."

**"High-uncertainty purchase intents where the customer knows what they physically need but cannot confidently name the SKU, compatibility, successor part, or best seller."**

---

*Document saved: 2026-09-07*
