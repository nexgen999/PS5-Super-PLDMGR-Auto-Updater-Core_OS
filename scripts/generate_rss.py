# scripts/generate_rss.py
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from scripts.config_rules import PATHS, BASE_URL

def generate_feeds_by_category(all_categories_data):
    """Génère les flux RSS et OPML globaux et par catégorie."""
    rss_dir = "rss"
    os.makedirs(rss_dir, exist_ok=True)

    global_rss_items = []

    for cat_key, cat_info in all_categories_data.items():
        cat_name = cat_info.get("name", cat_key.upper())
        items = cat_info.get("items", [])

        # Construction RSS spécifique à la catégorie
        rss_root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss_root, "channel")
        ET.SubElement(channel, "title").text = f"PS5 Store AIO - {cat_name}"
        ET.SubElement(channel, "link").text = BASE_URL
        ET.SubElement(channel, "description").text = f"Mises à jour automatiques pour la catégorie {cat_name}"

        # Construction OPML spécifique à la catégorie
        opml_root = ET.Element("opml", version="2.0")
        head = ET.SubElement(opml_root, "head")
        ET.SubElement(head, "title").text = f"PS5 Store AIO Feeds - {cat_name}"
        opml_body = ET.SubElement(opml_root, "body")

        for item in items:
            # Ajout RSS
            item_elem = ET.SubElement(channel, "item")
            ET.SubElement(item_elem, "title").text = item.get("name")
            ET.SubElement(item_elem, "link").text = item.get("url")
            ET.SubElement(item_elem, "description").text = item.get("description")
            ET.SubElement(item_elem, "pubDate").text = item.get("version", "v1.0.0")

            global_rss_items.append(item_elem)

            # Ajout OPML
            ET.SubElement(opml_body, "outline", {
                "text": item.get("name"),
                "title": item.get("name"),
                "type": "rss",
                "xmlUrl": item.get("url"),
                "description": item.get("description", "")
            })

        # Sauvegarde fichiers de la catégorie
        xml_str = minidom.parseString(ET.tostring(rss_root)).toprettyxml(indent="  ")
        with open(os.path.join(rss_dir, f"{cat_key}.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str)

        opml_str = minidom.parseString(ET.tostring(opml_root)).toprettyxml(indent="  ")
        with open(os.path.join(rss_dir, f"{cat_key}.opml"), "w", encoding="utf-8") as f:
            f.write(opml_str)
