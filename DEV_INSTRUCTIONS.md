# Dev Instructions — Build the Ultimate Site to Rank High in Google AI

**Goal:** Rank #1 in Google AI results and ChatGPT/Shopify listings for Norwegian spare parts.

---

## The Stack

```
COMPATIBILITY GRAPH (your data)
    ↓
FEED GENERATION (structured data)
    ↓
GOOGLE MERCHANT CENTER (distribution)
    ↓
WEB STORE (human interface)
```

---

## Repo #1: Feed Generation

### kiwoongeom/gmc-mcp (14 stars)

**What:** MCP server for Google Merchant Center — 126 tools

**Why:** Direct API access to Merchant Center. Query products, update feeds, check status.

```bash
pip install gmc-mcp
```

**Setup:**
1. Get Google Cloud service account
2. Enable Merchant Center API
3. Configure MCP server
4. Use tools to query/update feed

---

### lukesnowden/google-shopping-feed (68 stars)

**What:** PHP library for Google Shopping feed generation

**Why:** Generate compliant XML feeds from your product data.

```bash
composer require lukesnowden/google-shopping-feed
```

**Usage:**
```php
$feed = new GoogleShoppingFeed();
$feed->addItem([
    'id' => '00631200',
    'title' => 'Bosch 00631200 Circulation Pump',
    'description' => 'Compatible with SMS46MI08E...',
    'price' => '1129.00',
    'availability' => 'in_stock',
    'brand' => 'Bosch',
    'mpn' => '00631200',
]);
echo $feed->toXml();
```

---

## Repo #2: Web Store

### vercel/next.js (142K stars)

**What:** React framework for fast sites

**Why:** Fast, SEO-friendly, great for product pages.

```bash
npx create-next-app@latest my-store
```

**Key features:**
- Server-side rendering (SSR)
- Static generation (SSG)
- API routes
- Image optimization
- Built-in SEO

---

## Repo #3: Schema/Structured Data

### schemaorg/schemaorg (6K stars)

**What:** Schema.org definitions

**Why:** JSON-LD structured data for products.

**Use:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Bosch 00631200 Circulation Pump",
  "sku": "00631200",
  "brand": {"@type": "Brand", "name": "Bosch"},
  "offers": {
    "@type": "Offer",
    "price": "1129.00",
    "priceCurrency": "NOK",
    "availability": "https://schema.org/InStock"
  }
}
```

---

## Repo #4: Merchant Center Integration

### itallstartedwithaidea/advertising-hub (39 stars)

**What:** 14 platforms, 25+ AI agents

**Why:** Manage ads across Google, Meta, TikTok from one place.

---

## The Build Order

### Week 1: Feed Layer
```bash
# 1. Set up GMC account (free)
# 2. Install feed tool
pip install gmc-mcp
# 3. Create product feed with conversational attributes
# 4. Submit to Merchant Center
```

### Week 2: Web Store
```bash
# 1. Create Next.js store
npx create-next-app@latest norwegian-parts
# 2. Add product pages with JSON-LD
# 3. Add compatibility pages
# 4. Deploy to Vercel (free)
```

### Week 3: Content
```bash
# 1. Create "How to identify your model" pages
# 2. Create compatibility matrices
# 3. Add Q&A for each product
# 4. Add manuals/documentation
```

### Week 4: Test & Iterate
```bash
# 1. Test with Google AI Mode
# 2. Test with ChatGPT
# 3. Measure AI impression share
# 4. Optimize based on results
```

---

## The Feed Template

For each product, fill these fields:

```yaml
# Standard fields
id: "00631200"
title: "Bosch 00631200 Circulation Pump"
description: "OEM replacement for Bosch SMS46MI08E dishwasher..."
brand: "Bosch"
mpn: "00631200"
price: "1129.00"
availability: "in_stock"

# Conversational attributes (THE KEY)
question_and_answer:
  "Does this fit SMS46MI08E?": "Yes, direct replacement"
  "Does this replace 00611332?": "Yes, 00631200 supersedes 00611332"
  "Will I need an adapter?": "No, direct fit"

product_detail:
  - section: "Compatibility"
    attribute: "Compatible Models"
    value: "SMS46MI08E, SMS50MI08E"
  - section: "Electrical"
    attribute: "Voltage"
    value: "230V"
  - section: "Identification"
    attribute: "OEM Part Number"
    value: "00631200"

related_product:
  - type: "substitute"
    id: "00651956"
  - type: "accessory"
    id: "FILTER-001"
```

---

## The PDP Template

```
/grundfos-xyz-erstatning

[CRISP PRODUCT IMAGE]

Bosch 00631200 Circulation Pump

✓ Replaces: ABC-123 / ABC-124
✓ Fits systems: SMS46MI08E, SMS50MI08E
✓ Does NOT fit: SMS53MI08E (different connector)
✓ 230V / 50Hz
✓ In stock
✓ Ships from Norway
✓ Bergen: 1–2 days

[BUY]

---

Identification
OEM: 00631200
MPN: 00631200
EAN: 4005165123456

Fits
| Model | Fits? | Notes |
|-------|-------|-------|
| SMS46MI08E | Yes | Direct |
| SMS50MI08E | Yes | Direct |
| SMS53MI08E | No | Different connector |

How to Identify Yours
[images of label, connector, model plate]

Replacement Chain
2008 model → 2014 model → CURRENT SKU

FAQ
- Does this replace 00611332? Yes
- Do I need an adapter? No
- How do I verify my model? Check model plate inside door

Manual
[PDF link]
```

---

## Key Files to Create

```
my-store/
├── app/
│   ├── page.tsx                    # Homepage
│   ├── products/
│   │   └── [slug]/
│   │       └── page.tsx            # Product page
│   └── compatibility/
│       └── [model]/
│           └── page.tsx            # Compatibility page
├── components/
│   ├── ProductSchema.tsx           # JSON-LD structured data
│   ├── CompatibilityMatrix.tsx    # Fits/doesn't fit table
│   └── IdentificationGuide.tsx    # How to identify your model
└── lib/
    ├── products.ts                # Product data
    └── compatibility.ts          # Compatibility graph
```

---

## JSON-LD Template

```tsx
// components/ProductSchema.tsx
export function ProductSchema({ product }) {
  return (
    <script type="application/ld+json">
      {JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.title,
        "sku": product.mpn,
        "brand": {"@type": "Brand", "name": product.brand},
        "description": product.description,
        "offers": {
          "@type": "Offer",
          "price": product.price,
          "priceCurrency": "NOK",
          "availability": "https://schema.org/InStock"
        }
      })}
    </script>
  )
}
```

---

## Testing Checklist

- [ ] Google Merchant Center feed validated
- [ ] JSON-LD on every product page
- [ ] Compatibility matrix complete
- [ ] Q&A filled for each product
- [ ] Images: front, back, connector, label
- [ ] Manual/PDF attached
- [ ] Mobile responsive
- [ ] Page speed < 2s
- [ ] Test in Google AI Mode
- [ ] Test in ChatGPT

---

*Dev instructions: 2026-09-07*
