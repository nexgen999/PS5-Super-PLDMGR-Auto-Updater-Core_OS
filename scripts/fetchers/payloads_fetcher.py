import os
import re
import json
import hashlib
import subprocess
import urllib.request
from scripts.config_rules import PATHS, BASE_URL
from scripts.fetchers.utils import parse_opml_file
from scripts.cleaner import process_downloaded_payloads

def fetch_payloads_category(credits_set):
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

            if clean_xml_url.endswith(('.elf', '.bin', '.ffpfsc')):
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
                    print(f"    ⚠️ Échec source fixe ({title}) : {e}")

            if not downloaded and "github.com" in xml_url:
                repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                if repo_match:
                    repo = repo_match.group(1).rstrip('/')
                    repo_lower = repo.lower()
                    try:
                        release_json_str = subprocess.check_output(f"gh api repos/{repo}/releases/latest", shell=True).decode().strip()
                        release_data = json.loads(release_json_str)
                        
                        if release_data:
                            version = release_data.get('tag_name', 'v1.0.0')
                            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                            target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
                            os.makedirs(target_dir, exist_ok=True)

                            for asset in release_data.get('assets', []):
                                asset_url = asset.get('browser_download_url', '')
                                asset_name = asset.get('name', '')
                                if asset_name.lower().endswith(('.elf', '.bin', '.ffpfsc')):
                                    opener = urllib.request.build_opener()
                                    opener.addheaders = [('User-Agent', 'Mozilla/5.0'), ('Accept', 'application/octet-stream')]
                                    if os.environ.get('GITHUB_TOKEN'):
                                        opener.addheaders.append(('Authorization', f"token {os.environ.get('GITHUB_TOKEN')}"))
                                    urllib.request.install_opener(opener)
                                    urllib.request.urlretrieve(asset_url, os.path.join(target_dir, asset_name))
                                    downloaded = True
                    except Exception as e:
                        try:
                            target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), "v1.0.0")
                            os.makedirs(target_dir, exist_ok=True)
                            subprocess.call(f"gh release download --repo '{repo}' --dir '{target_dir}' --clobber 2>/dev/null", shell=True)
                            if os.listdir(target_dir):
                                downloaded = True
                        except Exception as sub_e:
                            print(f"    ⚠️ Échec fallback gh release download pour {repo}: {sub_e}")

            # --- GESTION FORGEJO / GITEA ROBUSTE (CONTOURNEMENT 401 PAR RAPPORT AUX URLS DIRECTES) ---
            if not downloaded and any(domain in xml_url for domain in ["git.", "codeberg.org", "gitlab.com", "gitea"]):
                try:
                    html_content = ""
                    # On tente de récupérer la page des releases, et si ça plante sur le 401, on attrape l'erreur pour ne pas crash
                    html_releases_url = f"{xml_url.rstrip('/')}/releases"
                    try:
                        req_html = urllib.request.Request(html_releases_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_html) as resp_html:
                            html_content = resp_html.read().decode('utf-8', errors='ignore')
                    except urllib.error.HTTPError:
                        # Si /releases bloque en 401, on tente d'interroger directement la page principale ou la page des tags
                        html_tags_url = f"{xml_url.rstrip('/')}/tag"
                        req_tags = urllib.request.Request(html_tags_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_tags) as resp_tags:
                            html_content = resp_tags.read().decode('utf-8', errors='ignore')

                    if html_content:
                        direct_links = re.findall(r'href="([^"]+\.(?:elf|bin|ffpfsc))"', html_content, re.IGNORECASE)
                        if direct_links:
                            direct_url = None
                            for link in direct_links:
                                if "releases/download" in link:
                                    direct_url = link
                                    break
                            if not direct_url:
                                direct_url = direct_links[0]

                            if not direct_url.startswith('http'):
                                base_uri = re.match(r'(https?://[^/]+)', xml_url).group(1)
                                direct_url = base_uri + direct_url
                            
                            f_name = direct_url.split('/')[-1].split('?')[0]
                            ver_match = re.search(r'/releases/download/([^/]+)/', direct_url)
                            version = ver_match.group(1) if ver_match else "latest"
                            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)

                            target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
                            os.makedirs(target_dir, exist_ok=True)
                            local_path = os.path.join(target_dir, f_name)
                            
                            opener = urllib.request.build_opener()
                            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                            urllib.request.install_opener(opener)
                            urllib.request.urlretrieve(direct_url, local_path)
                            
                            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                                downloaded = True
                                print(f"    ✅ Récupération réussie par contournement HTML pour {title}")

                except Exception as e:
                    print(f"    ⚠️ Erreur contournement Forgejo pour {xml_url} : {e}")
            # -----------------------------------------------------------------------------------------

            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version) if version != "Source-Fixe" else "Source-Fixe"
            target_dir = os.path.join(PATHS["categories"]["payloads"]["root"], cat_tech, title.replace(" ", "_"), version_clean)
            default_base_name = re.sub(r'[^a-zA-Z0-9._-]', '_', title)
            default_base_name = re.sub(r'_{2,}', '_', default_base_name).strip('_')

            eligible_binaries = process_downloaded_payloads(target_dir, repo_lower, default_base_name, version_clean)

            for main_file in eligible_binaries:
                full_path = os.path.join(target_dir, main_file)
                if not os.path.exists(full_path):
                    continue
                hasher = hashlib.sha256()
                with open(full_path, 'rb') as fb:
                    for chunk in iter(lambda: fb.read(4096), b""): hasher.update(chunk)

                credits_set.add(f"- **{author}** : [{title}]({xml_url})")
                display_name = os.path.splitext(main_file)[0].split('_v')[0]

                item_data = {
                    "name": display_name,
                    "filename": main_file,
                    "url": f"{BASE_URL}/{target_dir.replace(os.sep, '/')}/{main_file}",
                    "local_path": full_path,
                    "description": description if description else f"Payload {display_name} pour PS5",
                    "version": version,
                    "category": cat_display,
                    "checksum": hasher.hexdigest()
                }
                cat_list.append(item_data)
                all_flat.append(item_data)

        by_category[cat_tech] = {"name": cat_display, "items": cat_list}

    return by_category, all_flat
