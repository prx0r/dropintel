# The Merchant Center Goldmine — Complete Strategy

**Date:** 2026-09-07
**Status:** VALIDATED — Google built exactly what we need

---

## The Correction

> **Do not merely make the website "match Google's schema." Build the Merchant Center feed as the primary machine-facing product database, then make the website faithfully mirror it.**

Google's newest agentic fields (`related_product`, `question_and_answer`, `document_link`, `product_detail`) are **Merchant Center attributes**, not Schema.org markup.

---

## The Architecture

```
                    CANONICAL PRODUCT GRAPH
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      MERCHANT CENTER      SHOPIFY          WEBSITE
       deep feed DB        Catalog          human PDP
             │                │                │
             ▼                ▼                ▼
      Google Shopping      ChatGPT         Google/web
      Lens / Gemini        agents           crawlers
      AI Mode
             │                │
             └────────┬───────┘
                      ▼
                 BUYER INTENT
```

---

## The Spare-Parts Smoking Gun

Google's `related_product` attribute is **explicitly intended for conversational experiences such as AI Mode**.

Supported relationships:

```
required_part
substitute
different_brand
accessory
part_of_set
often_bought_with
```

Google specifically describes **spare parts and substitutes** as use cases.

**That is absurdly on-the-nose for GeoDrop.**

---

## Access Is Easy

### Conversational attributes

Use **now**. Available through:
- Primary feed
- Supplemental data source (recommended)
- Merchant API

Works in all countries. `related_product` explicitly works internationally.

### AI Max for Shopping

One-click upgrade if in beta. Currently **English-feed only** for title customization.

**Norway still works** — Norwegian is supported for Merchant Center, Shopping, Lens, Images.

---

## New X Accounts to Track

| Account | Why |
|---------|-----|
| **@AndrewLolk** | Sharpest strategic read on AI Max Shopping |
| **@mikeryanretail** | Analytical retail PPC operator, AI Mode ads |
| **@PPCKirk** | Kirk Williams, skeptical Shopping/feed operator |
| **@MenachemAni** | Ecommerce Google Ads, feeds, segmentation |
| **@GinnyMarvin** | Google Ads Liaison — platform changes |
| **@rustybrick** | Barry Schwartz, catches obscure Google tests |
| **@FeedArmy** | Emmanuel Flossie, identified 8 attributes |
| **@skuanalyzer** | Samuli Kesseli, implementation material |
| **@limelight** | Andy Warren, feed optimization |

---

## The Killer Loop

```
1. FIND BORING INSTALLED BASE
   Norwegian cabins, Finnish heat pumps, marine equipment

2. FIND BROKEN DIGITAL SUPPLY
   good local stock, bad feeds, bad images, no compatibility

3. INGEST SUPPLIER
   CSV / website / PDF / API

4. BUILD CANONICAL PRODUCT GRAPH
   entity, OEM, MPN, GTIN, compatibility, supersessions, specs

5. CREATE VISUAL CORPUS
   clean identification images, labels, connectors, old/new

6. GENERATE NATIVE-LANGUAGE SHOPIFY
   Norwegian PDP, NOK, local delivery

7. SYNDICATE
   Shopify Catalog, Merchant Center, free listings, Lens, Images

8. PAID PROVE
   Standard Shopping, small budget

9. HARVEST REAL INTENT
   search terms, returns, support questions

10. ENRICH GRAPH
    new aliases, Q&A, compatibility, related_product

11. REPEAT
```

---

## The Thesis (Final)

> **Google just converted the product feed from a list of products into a knowledge base for conversational shopping.**

**Own better product truth than competitors.**

`boring technical installed base + poor supplier digitization + native-language graph + excellent visual identification + Merchant Center conversational attributes + Shopify Catalog + tiny Shopping test`

---

*Document saved: 2026-09-07*
