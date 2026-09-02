# scripts/generate_rss.py
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from scripts.config_rules import BASE_URL

def build_rss_feed(data_store):
    base_rss_dir = "rss"
    os.makedirs(base_rss_dir, exist_ok=True)

    global_rss_root = ET.Element("rss", version="2.0")
    global_channel = ET.SubElement(global_rss_root, "channel")
    ET.SubElement(global_channel, "title").text = "PS5 Store AIO - Global Feed"
    ET.SubElement(global_channel, "link").text = BASE_URL
    ET.SubElement(global_channel, "description").text = "Flux RSS global de toutes les mises à jour du store PS5"

    for cat_key, cat_info in data_store.items():
        if not isinstance(cat_info, dict):
            continue
        
        sub_rss_dir = os.path.join(base_rss_dir, cat_key)
        os.makedirs(sub_rss_dir, exist_ok=True)

        cat_name = cat_info.get("name", cat_key.upper())
        items = cat_info.get("items", [])

        rss_root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss_root, "channel")
        ET.SubElement(channel, "title").text = f"PS5 Store AIO - {cat_name}"
        ET.SubElement(channel, "link").text = BASE_URL
        ET.SubElement(channel, "description").text = f"Mises à jour automatiques pour la catégorie {cat_name}"

        opml_root = ET.Element("opml", version="2.0")
        head = ET.SubElement(opml_root, "head")
        ET.SubElement(head, "title").text = f"PS5 Store Feeds - {cat_name}"
        opml_body = ET.SubElement(opml_root, "body")

        for item in items:
            item_elem = ET.SubElement(channel, "item")
            ET.SubElement(item_elem, "title").text = item.get("name")
            ET.SubElement(item_elem, "link").text = item.get("url")
            ET.SubElement(item_elem, "description").text = item.get("description")
            ET.SubElement(item_elem, "pubDate").text = item.get("version", "v1.0.0")

            g_item = ET.SubElement(global_channel, "item")
            ET.SubElement(g_item, "title").text = f"[{cat_name}] {item.get('name')}"
            ET.SubElement(g_item, "link").text = item.get("url")
            ET.SubElement(g_item, "description").text = item.get("description")
            ET.SubElement(g_item, "pubDate").text = item.get("version", "v1.0.0")

            ET.SubElement(opml_body, "outline", {
                "text": item.get("name"),
                "title": item.get("name"),
                "type": "rss",
                "xmlUrl": item.get("url"),
                "description": item.get("description", "")
            })

        xml_str = minidom.parseString(ET.tostring(rss_root)).toprettyxml(indent="  ")
        with open(os.path.join(sub_rss_dir, f"{cat_key}.xml"), "w", encoding="utf-8") as f:
            f.write(xml_str)

        opml_str = minidom.parseString(ET.tostring(opml_root)).toprettyxml(indent="  ")
        with open(os.path.join(sub_rss_dir, f"{cat_key}.opml"), "w", encoding="utf-8") as f:
            f.write(opml_str)

    global_xml_str = minidom.parseString(ET.tostring(global_rss_root)).toprettyxml(indent="  ")
    with open(os.path.join(base_rss_dir, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(global_xml_str)
