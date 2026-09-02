# scripts/fetchers/utils.py
import os
import re
import html
import json
import urllib.request
import subprocess
from scripts.config_rules import PATHS

def parse_opml_file(opml_path):
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

def fetch_assets_from_url(xml_url, title, description, author, allowed_extensions, category_folder="downloads"):
    assets_collected = []
    clean_url = xml_url.split('?')[0].lower()
    version = "v1.0.0"

    temp_dir = os.path.join(PATHS.get("archives_dir", "archives"), "temp_" + category_folder)
    os.makedirs(temp_dir, exist_ok=True)

    if clean_url.endswith(allowed_extensions):
        try:
            f_name = xml_url.split('/')[-1].split('?')[0]
            local_path = os.path.join(temp_dir, f_name)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(xml_url, local_path)
            
            assets_collected.append({
                "name": title,
                "filename": f_name,
                "url": xml_url,
                "local_path": local_path,
                "description": description or f"Fichier {title}",
                "version": version,
                "author": author
            })
        except Exception as e:
            print(f"    ⚠️ Erreur URL fixe ({title}): {e}")
        return assets_collected

    if "github.com" in xml_url:
        repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
        if repo_match:
            repo = repo_match.group(1).rstrip('/')
            try:
                res = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                data = json.loads(res)
                version = data.get('tagName', 'v1.0.0')
                for asset in data.get('assets', []):
                    asset_name = asset.get('name', '')
                    if asset_name.lower().endswith(allowed_extensions):
                        asset_url = asset.get('url') or asset.get('browser_download_url')
                        local_path = os.path.join(temp_dir, asset_name)
                        
                        try:
                            req_headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/octet-stream'}
                            if os.environ.get('GITHUB_TOKEN'):
                                req_headers['Authorization'] = f"token {os.environ.get('GITHUB_TOKEN')}"
                            
                            req = urllib.request.Request(asset_url, headers=req_headers)
                            with urllib.request.urlopen(req) as resp, open(local_path, 'wb') as out_file:
                                out_file.write(resp.read())
                        except Exception as dl_err:
                            print(f"    ⚠️ Téléchargement asset GitHub échoué ({asset_name}): {dl_err}")
                            continue

                        assets_collected.append({
                            "name": f"{title} ({asset_name})" if len(data.get('assets', [])) > 1 else title,
                            "filename": asset_name,
                            "url": asset_url,
                            "local_path": local_path,
                            "description": description or f"Asset {asset_name} pour {title}",
                            "version": version,
                            "author": author
                        })
            except Exception as e:
                print(f"    ⚠️ Erreur API GitHub pour {repo}: {e}")

    elif any(domain in xml_url for domain in ["git.", "codeberg.org", "gitlab.com", "gitea"]):
        try:
            api_match = re.search(r'(https?://[^/]+)/([^/]+/[^/]+)', xml_url)
            if api_match:
                base_domain = api_match.group(1)
                repo_path = api_match.group(2).rstrip('/')
                
                if "gitlab" in base_domain:
                    api_url = f"{base_domain}/api/v4/projects/{urllib.parse.quote(repo_path, safe='')}/releases"
                else:
                    api_url = f"{base_domain}/api/v1/repos/{repo_path}/releases"

                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    releases = json.loads(response.read().decode('utf-8'))
                    if releases:
                        latest = releases[0]
                        version = latest.get('tag_name', latest.get('tagName', 'v1.0.0'))
                        for asset in latest.get('assets', []):
                            asset_name = asset.get('name', '')
                            if asset_name.lower().endswith(allowed_extensions):
                                asset_url = asset.get('browser_download_url', asset.get('url', ''))
                                local_path = os.path.join(temp_dir, asset_name)
                                try:
                                    urllib.request.urlretrieve(asset_url, local_path)
                                except Exception as dl_err:
                                    print(f"    ⚠️ Erreur téléchargement asset Forgejo ({asset_name}): {dl_err}")
                                    continue

                                assets_collected.append({
                                    "name": title,
                                    "filename": asset_name,
                                    "url": asset_url,
                                    "local_path": local_path,
                                    "description": description or f"Asset {asset_name}",
                                    "version": version,
                                    "author": author
                                })
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"    🔒 Accès non autorisé (401) sur l'instance privée/protégée : {xml_url}")
            else:
                print(f"    ⚠️ Erreur HTTP {e.code} pour {xml_url}")
        except Exception as e:
            print(f"    ⚠️ Erreur connexion Forgejo/Git pour {xml_url}: {e}")

    return assets_collected
