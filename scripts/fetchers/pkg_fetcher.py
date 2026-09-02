# scripts/fetchers/pkg_fetcher.py
import os
import re
import json
import subprocess
import urllib.request
from scripts.config_rules import PATHS, BASE_URL

def fetch_pkg_category(credits_set):
    """Scraper 100% dédié aux packages PKG (liens directs ou assets GitHub .pkg)."""
    feed_dir = PATHS["categories"]["pkg"]["feed"]
    all_flat = []
    by_category = {}

    if not os.path.exists(feed_dir):
        return by_category, all_flat

    for opml_file in [f for f in os.listdir(feed_dir) if f.endswith('.opml')]:
        cat_tech = opml_file.replace('.opml', '').lower()
        cat_display = cat_tech.upper()
        cat_list = []
        
        # Lecture OPML (implémentation standardisée)
        entries = [] # Utilise ta fonction parse_opml_file ici
        
        for entry in entries:
            title = entry['title']
            xml_url = entry['xml_url']
            author = entry['author']
            description = entry['description']

            if not xml_url: continue

            version = "v1.0.0"
            assets_collected = []
            clean_url = xml_url.split('?')[0].lower()

            # 1. Lien direct .pkg
            if clean_url.endswith('.pkg'):
                f_name = xml_url.split('/')[-1].split('?')[0]
                assets_collected.append({
                    "name": title,
                    "filename": f_name,
                    "url": xml_url,
                    "description": description or f"Package PKG {title}",
                    "version": version,
                    "author": author,
                    "category": cat_display
                })
            # 2. Repository GitHub (recherche d'assets .pkg)
            elif "github.com" in xml_url:
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    try:
                        assets_json = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                        data_rel = json.loads(assets_json)
                        version = data_rel.get('tagName', 'v1.0.0')
                        for asset in data_rel.get('assets', []):
                            if asset.get('name', '').lower().endswith('.pkg'):
                                assets_collected.append({
                                    "name": title,
                                    "filename": asset.get('name'),
                                    "url": asset.get('url'),
                                    "description": description or f"PKG {asset.get('name')}",
                                    "version": version,
                                    "author": author,
                                    "category": cat_display
                                })
                    except: pass

            for item in assets_collected:
                credits_set.add(f"- **{author}** : [{title}]({xml_url})")
                cat_list.append(item)
                all_flat.append(item)

        by_category[cat_tech] = {"name": cat_display, "items": cat_list}
    return by_category, all_flat
