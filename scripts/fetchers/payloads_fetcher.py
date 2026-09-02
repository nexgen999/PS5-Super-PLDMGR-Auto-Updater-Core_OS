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

            # --- AJOUT DU SUPPORT FORGEJO / GITEA / GIT ---
            if not downloaded and any(domain in xml_url for domain in ["git.", "codeberg.org", "gitlab.com", "gitea"]):
                try:
                    if "git.etawen.dev" in xml_url:
                        api_repo_match = re.search(r'git\.etawen\.dev/([^/]+/[^/]+)', xml_url)
                        if api_repo_match:
                            repo_path = api_repo_match.group(1).rstrip('/')
                            api_url = f"https://git.etawen.dev/api/v1/repos/{repo_path}/releases"
                        else:
                            api_url = None
                    else:
                        api_match = re.search(r'(https?://[^/]+)/([^/]+/[^/]+)', xml_url)
                        if api_match:
                            base_domain = api_match.group(1)
                            repo_path = api_match.group(2).rstrip('/')
                            api_url = f"{base_domain}/api/v1/repos/{repo_path}/releases"
                        else:
                            api_url = None

                    if api_url:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        if "git.etawen.dev" in xml_url and os.environ.get('FORGEJO_TOKEN'):
                            headers['Authorization'] = f"token {os.environ.get('FORGEJO_TOKEN')}"

                        req = urllib.request.Request(api_url, headers=headers)
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
                                    if asset_name.lower().endswith(('.elf', '.bin', '.ffpfsc')):
                                        asset_req = urllib.request.Request(asset_url, headers=headers)
                                        with urllib.request.urlopen(asset_req) as resp_asset, open(os.path.join(target_dir, asset_name), 'wb') as f_out:
                                            f_out.write(resp_asset.read())
                                        downloaded = True
                except Exception as e:
                    print(f"    ⚠️ Erreur Forgejo/Gitea pour {xml_url} : {e}")
            # ---------------------------------------------

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
