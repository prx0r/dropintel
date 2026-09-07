"""Feed generator — converts product data to Google Merchant Center XML format.

Supports:
- Standard product fields (id, title, description, price, etc.)
- Conversational attributes (question_and_answer, product_detail, related_product)
- JSON-LD structured data
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Any


def generate_gmc_feed(products: list[dict], output_path: str):
    """Generate Google Merchant Center XML feed."""
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:g", "http://base.google.com/ns/1.0")
    
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Norwegian Spare Parts"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "description").text = "Compatible spare parts for Norwegian buildings"
    
    for product in products:
        item = ET.SubElement(channel, "item")
        
        # Standard fields
        ET.SubElement(item, "g:id").text = product.get("id", "")
        ET.SubElement(item, "title").text = product.get("title", "")
        ET.SubElement(item, "description").text = product.get("description", "")
        ET.SubElement(item, "g:brand").text = product.get("brand", "")
        ET.SubElement(item, "g:mpn").text = product.get("mpn", "")
        ET.SubElement(item, "g:price").text = product.get("price", "")
        ET.SubElement(item, "g:availability").text = product.get("availability", "in_stock")
        ET.SubElement(item, "link").text = product.get("url", "")
        ET.SubElement(item, "g:image_link").text = product.get("image", "")
        
        # Conversational attributes
        for qa in product.get("question_and_answer", []):
            q = ET.SubElement(item, "g:question_and_answer")
            ET.SubElement(q, "g:question").text = qa.get("question", "")
            ET.SubElement(q, "g:answer").text = qa.get("answer", "")
        
        for detail in product.get("product_detail", []):
            d = ET.SubElement(item, "g:product_detail")
            ET.SubElement(d, "g:section_name").text = detail.get("section", "")
            ET.SubElement(d, "g:attribute_name").text = detail.get("attribute", "")
            ET.SubElement(d, "g:attribute_value").text = detail.get("value", "")
        
        for rel in product.get("related_product", []):
            r = ET.SubElement(item, "g:related_product")
            ET.SubElement(r, "g:product_reference").text = rel.get("id", "")
            ET.SubElement(r, "g:relationship_type").text = rel.get("type", "")
    
    # Write XML
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    with open(output_path, "w") as f:
        f.write(xml_str)
    
    print(f"Generated feed: {output_path} ({len(products)} products)")


def generate_jsonld(products: list[dict]) -> list:
    """Generate JSON-LD structured data for products."""
    schemas = []
    for product in products:
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product.get("title", ""),
            "sku": product.get("mpn", ""),
            "brand": {"@type": "Brand", "name": product.get("brand", "")},
            "description": product.get("description", ""),
            "offers": {
                "@type": "Offer",
                "price": product.get("price", ""),
                "priceCurrency": "NOK",
                "availability": "https://schema.org/InStock"
            }
        }
        schemas.append(schema)
    return schemas
