# scripts/generate_rss.py

import os
import html
from datetime import datetime
from scripts.config_rules import PATHS, BASE_URL

def ensure_rss_directory():
    os.makedirs(PATHS["rss_dir"], exist_ok=True)

def build_rss_feed(data_store):
    """
    Génère rss/feed.xml contenant les dernières mises à jour de toutes les catégories.
    """
    ensure_rss_directory()
    rss_path = os.path.join(PATHS["rss_dir"], "feed.xml")
    
    now_rfc822 = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    items_xml = []

    # Rassemblement de tous les items plat
    all_items = []
    for cat_key in ["payloads", "pkg", "ffpfsc", "apps"]:
        if cat_key in data_store:
            _, flat_list = data_store[cat_key]
            for item in flat_list:
                all_items.append((cat_key, item))

    for cat_key, item in all_items:
        title = html.escape(item.get("name", "Inconnu"))
        link = html.escape(item.get("url", BASE_URL))
        desc = html.escape(item.get("description", ""))
        version = html.escape(item.get("version", "1.0.0"))
        category = html.escape(item.get("category", cat_key.upper()))
        
        item_xml = f"""    <item>
      <title>[{category}] {title} ({version})</title>
      <link>{link}</link>
      <description>{desc}</description>
      <pubDate>{now_rfc822}</pubDate>
      <guid isPermaLink="false">{link}#{version}</guid>
    </item>"""
        items_xml.append(item_xml)

    items_block = "\n".join(items_xml)

    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>AIO PS5 Store Updates</title>
    <link>{BASE_URL}</link>
    <description>Flux RSS automatisé des mises à jour du AIO PS5 Store</description>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
{items_block}
  </channel>
</rss>"""

    with open(rss_path, 'w', encoding='utf-8') as f:
        f.write(rss_content)

    print("✅ Génération du flux RSS (rss/feed.xml) terminée.")
