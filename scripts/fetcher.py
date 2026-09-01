# scripts/fetcher.py

import os
import re
import json
import html
import hashlib
import subprocess
import urllib.request
from scripts.config_rules import PATHS, BASE_URL
from scripts.cleaner import process_downloaded_payloads

def parse_opml_file(opml_path):
    """Lit un fichier OPML et retourne la liste des entrées."""
    items = []
    if not os.path.exists(opml_path):
        return items
    with open(opml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for outline in re.findall(r'<outline\s+([^>]+)/>', content):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
        items.append({
            'title': html.unescape(attrs.get('title', attrs.get('text', 'Inconnu'))),
            'xml_url': attrs.get('xmlUrl', '').strip(),
            'author': html.unescape(attrs.get('author', 'Inconnu')),
            'description': html.unescape(attrs.get('description', ''))
        })
    return items

def fetch_payloads(credits_set):
    """Parse et télécharge tous les payloads (.elf / .bin)."""
    payload_feed_dir = PATHS["categories"]["payloads"]["feed"]
    all_flat = []
    by_category = {}

    if not os.path.exists(payload_feed_dir):
        return by_category, all_flat

    for opml_file in [f for f in os.listdir(payload_feed_dir) if f.endswith('.opml')]:
        cat_tech = opml_file.replace('.opml', '')
        cat_display = cat_tech.replace('_', ' ').title()
        if "Hen" in cat_display: cat_display = cat_display.replace("Hen", "HEN")
        if cat_display.startswith("Ps5 "): cat_display = cat_display.replace("Ps5 ", "PS5 ")

        cat_list = []
        entries = parse_opml_file(os.path.join(payload_feed_dir, opml_file))

        for entry in entries:
            title = entry['title']
            xml_url = entry['xml_url']
            author = entry['author']
            description = entry['description']

            if not xml_url or "ps4" in title.lower() or "ps4" in description.lower():
                continue

            version = "v1.0.0"
            downloaded = False
            clean_xml_url = xml_url.split('?')[0].lower()
            repo_lower = ""

            # --- Source Fixe Directe ---
            if clean_xml_url.endswith('.elf') or clean_xml_url.endswith('.bin'):
                try:
                    version = "Source-Fixe"
                    version_clean = "Source-Fixe"
                    target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
                    os.makedirs(target_dir, exist_ok=True)
                    f_name = xml_url.split('?')[0].split('/')[-1]
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(xml_url, os.path.join(target_dir, f_name))
                    downloaded = True
                except Exception as e:
                    print(f"   ⚠️ Échec source fixe ({title}) : {e}")

            # --- Release GitHub ---
            if not downloaded and "github.com" in xml_url:
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    repo_lower = repo.lower()
                    try:
                        res_tag = subprocess.check_output(f"gh release list --repo {repo} --limit 1 --json tagName --jq '.[0].tagName'", shell=True).decode().strip()
                        if res_tag: 
                            version = res_tag
                        else:
                            res_tag = subprocess.check_output(f"gh repo view {repo} --json latestRelease --jq '.latestRelease.tagName'", shell=True).decode().strip()
                            if res_tag: version = res_tag
                    except: pass

                    version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                    target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
                    os.makedirs(target_dir, exist_ok=True)

                    try:
                        subprocess.call(f"gh release download '{version}' --repo '{repo}' --dir '{target_dir}' --clobber 2>/dev/null", shell=True)
                    except: pass

            # --- Release Forgejo / Gitea ---
            if not downloaded and "git.etawen.dev" in xml_url:
                try:
                    api_repo_match = re.search(r'git\.etawen\.dev/([^/]+/[^/]+)', xml_url)
                    if api_repo_match:
                        repo_path = api_repo_match.group(1).rstrip('/')
                        api_url = f"https://git.etawen.dev/api/v1/repos/{repo_path}/releases"
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response:
                            releases_data = json.loads(response.read().decode('utf-8'))
                            if releases_data:
                                latest_release = releases_data[0]
                                version = latest_release.get('tag_name', 'v1.0.0')
                                version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                                target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
                                os.makedirs(target_dir, exist_ok=True)
                                
                                for asset in latest_release.get('assets', []):
                                    asset_url = asset.get('browser_download_url', '')
                                    asset_name = asset.get('name', '')
                                    if asset_name.lower().endswith(('.elf', '.bin')):
                                        urllib.request.urlretrieve(asset_url, os.path.join(target_dir, asset_name))
                                        break
                except: pass

            # --- Traitement, Nettoyage & Construction du résultat ---
            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version) if version != "Source-Fixe" else "Source-Fixe"
            target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
            default_base_name = re.sub(r'[^a-zA-Z0-9._-]', '_', title)
            default_base_name = re.sub(r'_{2,}', '_', default_base_name).strip('_')

            eligible_binaries = process_downloaded_payloads(target_dir, repo_lower, default_base_name, version_clean)

            for main_file in eligible_binaries:
                full_path = os.path.join(target_dir, main_file)
                hasher = hashlib.sha256()
                with open(full_path, 'rb') as fb:
                    for chunk in iter(lambda: fb.read(4096), b""): hasher.update(chunk)

                credits_set.add(f"- **{author}** : [{title}]({xml_url})")
                display_name = os.path.splitext(main_file)[0].split('_v')[0]

                item_data = {
                    "name": display_name,
                    "filename": main_file,
                    "url": f"{BASE_URL}/{target_dir.replace(os.sep, '/')}/{main_file}",
                    "description": description if description else f"Payload {display_name} pour PS5",
                    "version": version,
                    "category": cat_display,
                    "checksum": hasher.hexdigest()
                }
                cat_list.append(item_data)
                all_flat.append(item_data)

        by_category[cat_tech] = {"name": cat_display, "items": cat_list}

    return by_category, all_flat

def fetch_generic_category(category_key, item_field, file_ext, credits_set):
    """Fonction générique pour récupérer les éléments de PKG, FFPFSC et APPS."""
    feed_dir = PATHS["categories"][category_key]["feed"]
    all_flat = []
    by_category = {}

    if not os.path.exists(feed_dir):
        return by_category, all_flat

    for opml_file in [f for f in os.listdir(feed_dir) if f.endswith('.opml')]:
        cat_tech = opml_file.replace('.opml', '').lower()
        cat_display = cat_tech.upper()
        cat_list = []
        entries = parse_opml_file(os.path.join(feed_dir, opml_file))

        for entry in entries:
            title = entry['title']
            xml_url = entry['xml_url']
            author = entry['author']
            description = entry['description']

            if not xml_url: continue

            version = "v1.0.0"
            if "github.com" in xml_url and category_key == "apps":
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    try:
                        assets_json = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                        data_rel = json.loads(assets_json)
                        version = data_rel.get('tagName', 'v1.0.0')
                        assets = data_rel.get('assets', [])

                        if assets:
                            for asset in assets:
                                asset_url = asset.get('url', '')
                                asset_name = asset.get('name', '')
                                credits_set.add(f"- **{author}** : [{title}]({xml_url})")
                                item_data = {
                                    "name": f"{title} ({asset_name})",
                                    "filename": asset_name,
                                    "url": asset_url,
                                    "description": description if description else f"Asset {asset_name} pour {title}",
                                    "version": version,
                                    "author": author,
                                    "category": cat_display
                                }
                                cat_list.append(item_data)
                                all_flat.append(item_data)
                            continue
                    except: pass

            elif "github.com" in xml_url and not xml_url.endswith(file_ext):
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    try:
                        assets_json = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                        data_rel = json.loads(assets_json)
                        version = data_rel.get('tagName', 'v1.0.0')
                        for asset in data_rel.get('assets', []):
                            if asset.get('name', '').lower().endswith(file_ext):
                                xml_url = asset.get('url', xml_url)
                                break
                    except: version = "v1.0.0"
            else:
                v_match = re.search(r'v(\d+[\.\d+]*)', xml_url, re.IGNORECASE)
                version = f"v{v_match.group(1)}" if v_match else "v1.0.0"

            raw_filename = xml_url.split('/')[-1].split('?')[0]
            if not raw_filename.lower().endswith(file_ext):
                raw_filename = f"{title}{file_ext}"

            credits_set.add(f"- **{author}** : [{title}]({xml_url})")
            item_data = {
                "name": title,
                "filename": raw_filename,
                "url": xml_url,
                "description": description if description else f"Fichier {title}",
                "version": version,
                "author": author,
                "category": cat_display
            }
            cat_list.append(item_data)
            all_flat.append(item_data)

        by_category[cat_tech] = {"name": cat_display, "items": cat_list}

    return by_category, all_flat
