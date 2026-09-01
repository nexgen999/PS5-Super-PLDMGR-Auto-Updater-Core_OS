import os
import sys
import json
import re
import hashlib
import subprocess
import urllib.request
import zipfile
import html

# --- Détection dynamique pour l'universalité (Forks / Local) ---
github_repo_env = os.environ.get('GITHUB_REPOSITORY', 'nexgen999/PS5-Super-PLDMGR-Auto-Updater')
if '/' in github_repo_env:
    GITHUB_USER, REPO_NAME = github_repo_env.split('/', 1)
else:
    GITHUB_USER, REPO_NAME = 'nexgen999', github_repo_env

BASE_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}"

# --- Structure des Chemins ---
FEED_DIR = "feed"
PAYLOAD_FEED_DIR = os.path.join(FEED_DIR, "payloads")
PKG_FEED_DIR = os.path.join(FEED_DIR, "pkg")
FFPFSC_FEED_DIR = os.path.join(FEED_DIR, "ffpfsc")
APPS_FEED_DIR = os.path.join(FEED_DIR, "apps")

JSON_DIR = "json"
PAYLOAD_JSON_DIR = os.path.join(JSON_DIR, "payloads")
PKG_JSON_DIR = os.path.join(JSON_DIR, "pkg")
FFPFSC_JSON_DIR = os.path.join(JSON_DIR, "ffpfsc")
APPS_JSON_DIR = os.path.join(JSON_DIR, "apps")

RSS_DIR = "rss"
PAYLOADS_ROOT = "payloads"

# Création des dossiers de sortie
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(PAYLOAD_JSON_DIR, exist_ok=True)
os.makedirs(PKG_JSON_DIR, exist_ok=True)
os.makedirs(FFPFSC_JSON_DIR, exist_ok=True)
os.makedirs(APPS_JSON_DIR, exist_ok=True)
os.makedirs(RSS_DIR, exist_ok=True)
os.makedirs(PAYLOADS_ROOT, exist_ok=True)

all_payloads_flat_list = []
all_pkgs_flat_list = []
all_ffpfsc_flat_list = []
all_apps_flat_list = []
credits_list = set()

print(f"=== Début de la synchronisation ({GITHUB_USER}/{REPO_NAME}) ===")

# =========================================================================
# 1. TRAITEMENT DES PAYLOADS (.ELF / .BIN)
# =========================================================================
print("\n⚡ Traitement des Payloads...")

if os.path.exists(PAYLOAD_FEED_DIR):
    for opml_file in [f for f in os.listdir(PAYLOAD_FEED_DIR) if f.endswith('.opml')]:
        cat_tech_name = opml_file.replace('.opml', '')
        cat_display_name = cat_tech_name.replace('_', ' ').title()
        if "Hen" in cat_display_name: cat_display_name = cat_display_name.replace("Hen", "HEN")
        if cat_display_name.startswith("Ps5 "): cat_display_name = cat_display_name.replace("Ps5 ", "PS5 ")
        
        category_payloads_list = []
        with open(os.path.join(PAYLOAD_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
            content = f.read()

        for outline in re.findall(r'<outline\s+([^>]+)/>', content):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
            title = html.unescape(attrs.get('title', attrs.get('text', 'Inconnu')))
            xml_url = attrs.get('xmlUrl', '').strip()
            author = html.unescape(attrs.get('author', 'Inconnu'))
            description = html.unescape(attrs.get('description', ''))

            if not xml_url or "ps4" in title.lower() or "ps4" in description.lower():
                continue

            version = "v1.0.0"
            downloaded = False
            clean_xml_url = xml_url.split('?')[0].lower()
            
            # Sources Fixes
            if clean_xml_url.endswith('.elf') or clean_xml_url.endswith('.bin'):
                try:
                    version = "Source-Fixe"
                    target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version)
                    os.makedirs(target_dir, exist_ok=True)
                    f_name = xml_url.split('?')[0].split('/')[-1]
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(xml_url, os.path.join(target_dir, f_name))
                    downloaded = True
                except Exception as e: pass

            # Releases GitHub
            repo_lower = ""
            if not downloaded and "github.com" in xml_url:
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    repo_lower = repo.lower()
                    try:
                        res_tag = subprocess.check_output(f"gh release list --repo {repo} --limit 1 --json tagName --jq '.[0].tagName'", shell=True).decode().strip()
                        if res_tag: version = res_tag
                    except: pass
                    
                    version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                    target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                    os.makedirs(target_dir, exist_ok=True)

                    try:
                        subprocess.call(f"gh release download '{version}' --repo '{repo}' --dir '{target_dir}' --clobber 2>/dev/null", shell=True)
                        files_downloaded = os.listdir(target_dir)
                        for f in files_downloaded:
                            if not (f.lower().endswith('.elf') or f.lower().endswith('.bin')):
                                try: os.remove(os.path.join(target_dir, f))
                                except: pass
                        if os.listdir(target_dir): downloaded = True
                    except: pass

            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version) if version != "Source-Fixe" else "Source-Fixe"
            target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
            files_in_dir = os.listdir(target_dir) if os.path.exists(target_dir) else []

            for main_file in [f for f in files_in_dir if f.lower().endswith(('.elf', '.bin'))]:
                full_path = os.path.join(target_dir, main_file)
                hasher = hashlib.sha256()
                with open(full_path, 'rb') as fb:
                    for chunk in iter(lambda: fb.read(4096), b""): hasher.update(chunk)
                
                credits_list.add(f"- **{author}** : [{title}]({xml_url})")
                item_data = {
                    "name": title,
                    "filename": main_file,
                    "url": f"{BASE_URL}/{target_dir.replace(os.sep, '/')}/{main_file}",
                    "description": description if description else f"Payload {title} pour PS5",
                    "version": version,
                    "category": cat_display_name,
                    "checksum": hasher.hexdigest()
                }
                category_payloads_list.append(item_data)
                all_payloads_flat_list.append(item_data)

        with open(os.path.join(PAYLOAD_JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_cat:
            json.dump({"name": cat_display_name, "payloads": category_payloads_list}, out_cat, indent=2, ensure_ascii=False)

with open(os.path.join(JSON_DIR, "payloads.json"), 'w', encoding='utf-8') as out_glob:
    json.dump({"name": "AIO Store Payloads", "payloads": all_payloads_flat_list}, out_glob, indent=2, ensure_ascii=False)


# =========================================================================
# 2. TRAITEMENT DES PACKAGES PKG (.PKG)
# =========================================================================
print("\n📦 Traitement des Packages PKG...")

if os.path.exists(PKG_FEED_DIR):
    for opml_file in [f for f in os.listdir(PKG_FEED_DIR) if f.endswith('.opml')]:
        cat_tech_name = opml_file.replace('.opml', '').lower()
        cat_display_name = cat_tech_name.upper()
        category_pkgs_list = []

        with open(os.path.join(PKG_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
            content = f.read()

        for outline in re.findall(r'<outline\s+([^>]+)/>', content):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
            title = html.unescape(attrs.get('title', attrs.get('text', 'Inconnu')))
            xml_url = attrs.get('xmlUrl', '').strip()
            author = html.unescape(attrs.get('author', 'Inconnu'))
            description = html.unescape(attrs.get('description', ''))

            if not xml_url: continue

            # Détection GitHub Release dynamique pour .pkg
            if "github.com" in xml_url and not xml_url.endswith('.pkg'):
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    try:
                        assets_json = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                        data_rel = json.loads(assets_json)
                        version = data_rel.get('tagName', 'v1.0.0')
                        for asset in data_rel.get('assets', []):
                            if asset.get('name', '').lower().endswith('.pkg'):
                                xml_url = asset.get('url', xml_url)
                                break
                    except: version = "v1.0.0"
            else:
                v_match = re.search(r'v(\d+[\.\d+]*)', xml_url, re.IGNORECASE)
                version = f"v{v_match.group(1)}" if v_match else "v1.0.0"

            raw_filename = xml_url.split('/')[-1].split('?')[0]
            if not raw_filename.lower().endswith('.pkg'): raw_filename = f"{title}.pkg"

            credits_list.add(f"- **{author}** : [{title}]({xml_url})")
            item_data = {
                "name": title, "filename": raw_filename, "url": xml_url,
                "description": description if description else f"Package {title} pour PS5",
                "version": version, "author": author, "category": cat_display_name
            }
            category_pkgs_list.append(item_data)
            all_pkgs_flat_list.append(item_data)

        with open(os.path.join(PKG_JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_pkg_cat:
            json.dump({"name": cat_display_name, "packages": category_pkgs_list}, out_pkg_cat, indent=2, ensure_ascii=False)

with open(os.path.join(JSON_DIR, "pkg.json"), 'w', encoding='utf-8') as out_pkg_glob:
    json.dump({"name": "AIO Store PKG", "packages": all_pkgs_flat_list}, out_pkg_glob, indent=2, ensure_ascii=False)


# =========================================================================
# 3. TRAITEMENT DES FICHIERS FFPFSC (.FFPFSC)
# =========================================================================
print("\n📄 Traitement des Fichiers FFPFSC...")

if os.path.exists(FFPFSC_FEED_DIR):
    for opml_file in [f for f in os.listdir(FFPFSC_FEED_DIR) if f.endswith('.opml')]:
        cat_tech_name = opml_file.replace('.opml', '').lower()
        cat_display_name = cat_tech_name.upper()
        category_ffpfsc_list = []

        with open(os.path.join(FFPFSC_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
            content = f.read()

        for outline in re.findall(r'<outline\s+([^>]+)/>', content):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
            title = html.unescape(attrs.get('title', attrs.get('text', 'Inconnu')))
            xml_url = attrs.get('xmlUrl', '').strip()
            author = html.unescape(attrs.get('author', 'Inconnu'))
            description = html.unescape(attrs.get('description', ''))

            if not xml_url: continue

            # Scraping dynamique GitHub Release si lien global
            if "github.com" in xml_url and not xml_url.endswith('.ffpfsc'):
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    try:
                        assets_json = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                        data_rel = json.loads(assets_json)
                        version = data_rel.get('tagName', 'v1.0.0')
                        for asset in data_rel.get('assets', []):
                            if asset.get('name', '').lower().endswith('.ffpfsc'):
                                xml_url = asset.get('url', xml_url)
                                break
                    except: version = "v1.0.0"
            else:
                v_match = re.search(r'v(\d+[\.\d+]*)', xml_url, re.IGNORECASE)
                version = f"v{v_match.group(1)}" if v_match else "v1.0.0"

            raw_filename = xml_url.split('/')[-1].split('?')[0]
            if not raw_filename.lower().endswith('.ffpfsc'): raw_filename = f"{title}.ffpfsc"

            credits_list.add(f"- **{author}** : [{title}]({xml_url})")
            item_data = {
                "name": title, "filename": raw_filename, "url": xml_url,
                "description": description if description else f"Fichier FFPFSC {title}",
                "version": version, "author": author, "category": cat_display_name
            }
            category_ffpfsc_list.append(item_data)
            all_ffpfsc_flat_list.append(item_data)

        with open(os.path.join(FFPFSC_JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_ff_cat:
            json.dump({"name": cat_display_name, "files": category_ffpfsc_list}, out_ff_cat, indent=2, ensure_ascii=False)

with open(os.path.join(JSON_DIR, "ffpfsc.json"), 'w', encoding='utf-8') as out_ffpfsc:
    json.dump({"name": "AIO Store FFPFSC", "files": all_ffpfsc_flat_list}, out_ffpfsc, indent=2, ensure_ascii=False)


# =========================================================================
# 4. TRAITEMENT DES APPLICATIONS (LISTE TOUS LES ASSETS DU DEPOT)
# =========================================================================
print("\n📱 Traitement des Applications APPS (Scraping de tous les assets)...")

if os.path.exists(APPS_FEED_DIR):
    for opml_file in [f for f in os.listdir(APPS_FEED_DIR) if f.endswith('.opml')]:
        cat_tech_name = opml_file.replace('.opml', '').lower()
        cat_display_name = cat_tech_name.upper()
        category_apps_list = []

        with open(os.path.join(APPS_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
            content = f.read()

        for outline in re.findall(r'<outline\s+([^>]+)/>', content):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
            title = html.unescape(attrs.get('title', attrs.get('text', 'Inconnu')))
            xml_url = attrs.get('xmlUrl', '').strip()
            author = html.unescape(attrs.get('author', 'Inconnu'))
            description = html.unescape(attrs.get('description', ''))

            if not xml_url: continue

            # Extraire TOUS les fichiers de la release sur GitHub
            if "github.com" in xml_url:
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
                                credits_list.add(f"- **{author}** : [{title}]({xml_url})")
                                item_data = {
                                    "name": f"{title} ({asset_name})",
                                    "filename": asset_name,
                                    "url": asset_url,
                                    "description": description if description else f"Asset {asset_name} pour {title}",
                                    "version": version,
                                    "author": author,
                                    "category": cat_display_name
                                }
                                category_apps_list.append(item_data)
                                all_apps_flat_list.append(item_data)
                            continue
                    except Exception as e:
                        pass

            # Fallback direct link
            raw_filename = xml_url.split('/')[-1].split('?')[0]
            v_match = re.search(r'v(\d+[\.\d+]*)', raw_filename, re.IGNORECASE)
            version = f"v{v_match.group(1)}" if v_match else "v1.0.0"

            credits_list.add(f"- **{author}** : [{title}]({xml_url})")
            item_data = {
                "name": title, "filename": raw_filename, "url": xml_url,
                "description": description if description else f"Application {title}",
                "version": version, "author": author, "category": cat_display_name
            }
            category_apps_list.append(item_data)
            all_apps_flat_list.append(item_data)

        with open(os.path.join(APPS_JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_app_cat:
            json.dump({"name": cat_display_name, "apps": category_apps_list}, out_app_cat, indent=2, ensure_ascii=False)

with open(os.path.join(JSON_DIR, "apps.json"), 'w', encoding='utf-8') as out_apps:
    json.dump({"name": "AIO Store Apps", "apps": all_apps_flat_list}, out_apps, indent=2, ensure_ascii=False)


# =========================================================================
# 5. GENERATION RSS PAR CATEGORIE & DISCORD + README.MD
# =========================================================================

print("\n📡 Génération des flux RSS (Dédiés + Global Discord)...")

def generate_rss_xml(filename, title, description, items):
    filepath = os.path.join(RSS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n  <channel>\n')
        f.write(f'    <title>{html.escape(title)}</title>\n')
        f.write(f'    <link>{BASE_URL}/</link>\n')
        f.write(f'    <description>{html.escape(description)}</description>\n')
        for item in items:
            f.write('    <item>\n')
            f.write(f'      <title>{html.escape(item.get("name", "Inconnu"))} ({html.escape(item.get("version", "v1.0.0"))})</title>\n')
            f.write(f'      <link>{html.escape(item.get("url", ""))}</link>\n')
            desc = item.get("description", "")
            if "checksum" in item:
                desc += f" - Checksum: {item['checksum']}"
            f.write(f'      <description>{html.escape(desc)}</description>\n')
            f.write('    </item>\n')
        f.write('  </channel>\n</rss>')

# Génération des 4 RSS dédiés
generate_rss_xml("payloads.xml", "PS5 Payloads Radar", "Suivi des derniers Payloads PS5", all_payloads_flat_list)
generate_rss_xml("pkg.xml", "PS5 PKG Radar", "Suivi des derniers Packages PKG PS5", all_pkgs_flat_list)
generate_rss_xml("ffpfsc.xml", "PS5 FFPFSC Radar", "Suivi des derniers Fichiers FFPFSC", all_ffpfsc_flat_list)
generate_rss_xml("apps.xml", "PS5 Apps Radar", "Suivi des dernières Applications PS5", all_apps_flat_list)

# RSS Global dédié à Discord (Combine TOUT)
all_items_combined = all_payloads_flat_list + all_pkgs_flat_list + all_ffpfsc_flat_list + all_apps_flat_list
generate_rss_xml("feed.xml", "PS5 Mini-Store Global (Discord Feed)", "Flux complet récapitulatif pour webhooks Discord", all_items_combined)

# Génération de l'OPML Global
with open(os.path.join(RSS_DIR, "store-global.opml"), "w", encoding="utf-8") as opml_out:
    opml_out.write('<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head>\n    <title>PS5 Store Global Radar</title>\n  </head>\n  <body>\n')
    for row in sorted(list(credits_list)):
        match = re.search(r'\*\*([^*]+)\*\*\s*:\s*\[([^\]]+)\]\(([^)]+)\)', row)
        if match:
            author_name, title_name, raw_url = match.group(1), match.group(2), match.group(3)
            opml_out.write(f'    <outline text="{html.escape(title_name)}" title="{html.escape(title_name)}" type="rss" xmlUrl="{html.escape(raw_url)}" author="{html.escape(author_name)}"/>\n')
    opml_out.write('  </body>\n</opml>')

print("📝 Génération du README.md...")
with open("README.md", "w", encoding="utf-8") as r_file:
    r_file.write("![Banner](assets/banner.png)\n\n")
    r_file.write("# 🎮 PS5 Payload Manager & Mini-Store\n\n")
    r_file.write("Bienvenue sur cet écosystème automatisé pour la scène jailbreak PS5 !\n\n")
    r_file.write(f"🌐 **Site Web Vitrine :** [Visiter le site]({BASE_URL}/index.html)\n\n")
    
    r_file.write("## 🔗 URLs Fixes des Stores JSON\n")
    r_file.write(f"* **Payloads Store JSON :** `{BASE_URL}/json/payloads.json`\n")
    r_file.write(f"* **Packages PKG Store JSON :** `{BASE_URL}/json/pkg.json`\n")
    r_file.write(f"* **FFPFSC Store JSON :** `{BASE_URL}/json/ffpfsc.json`\n")
    r_file.write(f"* **Apps Store JSON :** `{BASE_URL}/json/apps.json`\n\n")
    
    r_file.write("## 📡 Flux RSS & OPML (Webhooks Discord & Lecteurs RSS)\n")
    r_file.write(f"* 🤖 **Feed Global (Discord Webhook) :** `{BASE_URL}/rss/feed.xml`\n")
    r_file.write(f"* 📁 **Import OPML Global :** `{BASE_URL}/rss/store-global.opml`\n")
    r_file.write(f"* ⚡ **Flux RSS Payloads :** `{BASE_URL}/rss/payloads.xml`\n")
    r_file.write(f"* 📦 **Flux RSS PKG :** `{BASE_URL}/rss/pkg.xml`\n")
    r_file.write(f"* 📄 **Flux RSS FFPFSC :** `{BASE_URL}/rss/ffpfsc.xml`\n")
    r_file.write(f"* 📱 **Flux RSS Apps :** `{BASE_URL}/rss/apps.xml`\n\n")

r_file.write("## 📦 Archives AIO Releases (Dernières Versions)\n")
    r_file.write(f"* 🌐 **PS5 Ultimate Pack (TOUT INCLUS) (.zip) :** [Télécharger](https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/latest/PS5_ultimate_pack_aio_latest.zip)\n")
    r_file.write(f"* 🚀 **AIO Payloads Offline (.zip) :** [Télécharger](https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/latest/PS5_payloads_aio_latest.zip)\n")
    r_file.write(f"* 📦 **AIO PKG Offline (.zip) :** [Télécharger](https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/latest/PS5_pkg_aio_latest.zip)\n")
    r_file.write(f"* 📄 **AIO FFPFSC Offline (.zip) :** [Télécharger](https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/latest/PS5_ffpfsc_aio_latest.zip)\n")
    r_file.write(f"* 📱 **AIO Apps Offline (.zip) :** [Télécharger](https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/latest/PS5_apps_aio_latest.zip)\n\n")
    
    r_file.write("---\n\n")
    r_file.write("## 🤝 Crédits & Remerciements\n")
    r_file.write("\n".join(sorted(list(credits_list))) + "\n\n")
    r_file.write("---\n")
    r_file.write("*Dépôt 100% autonome géré par GitHub Actions.*\n")

print("=== Synchronisation terminée ===")
