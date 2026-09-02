import os
import re
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

def fetch_repository_assets(xml_url, title, description, author, temp_dir, allowed_extensions=('.elf', '.bin', '.pkg', '.zip')):
    """
    Récupère les assets d'un dépôt (GitHub, Forgejo, etc.) à partir d'une URL OPML/RSS
    et retourne la liste des fichiers collectés.
    """
    assets_collected = []
    
    # 1. Gestion des dépôts GitHub (via l'API Releases)
    if "github.com" in xml_url:
        try:
            github_match = re.search(r'github\.com/([^/]+/[^/]+?)(?:/releases|\.atom|/|$)', xml_url)
            if not github_match:
                github_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
                
            if github_match:
                repo_path = github_match.group(1).rstrip('/')
                api_url = f"https://api.github.com/repos/{repo_path}/releases/latest"
                
                headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'}
                github_token = os.environ.get('GITHUB_TOKEN')
                if github_token:
                    headers['Authorization'] = f"token {github_token}"
                
                req = urllib.request.Request(api_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    release_data = json.loads(response.read().decode('utf-8'))
                    version = release_data.get('tag_name', 'v1.0.0')
                    
                    for asset in release_data.get('assets', []):
                        asset_name = asset.get('name', '')
                        asset_url = asset.get('browser_download_url', '')
                        clean_name = asset_name.lower()
                        
                        if clean_name.endswith(allowed_extensions):
                            local_path = os.path.join(temp_dir, asset_name)
                            try:
                                asset_req = urllib.request.Request(asset_url, headers=headers)
                                with urllib.request.urlopen(asset_req) as resp_asset, open(local_path, 'wb') as f_out:
                                    f_out.write(resp_asset.read())
                            except Exception as dl_err:
                                print(f"    ⚠️ Erreur téléchargement asset GitHub ({asset_name}): {dl_err}")
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
        except Exception as e:
            print(f"    ⚠️ Erreur connexion GitHub pour {xml_url}: {e}")

    # 2. Gestion des dépôts Forgejo / Gitea / GitLab
    elif any(domain in xml_url for domain in ["git.", "codeberg.org", "gitlab.com", "gitea"]):
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
                    base_domain, repo_path = api_match.group(1), api_match.group(2).rstrip('/')
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
                        
                        for asset in latest_release.get('assets', []):
                            asset_name = asset.get('name', '')
                            asset_url = asset.get('browser_download_url', '')
                            clean_name = asset_name.lower()
                            
                            if clean_name.endswith(allowed_extensions):
                                local_path = os.path.join(temp_dir, asset_name)
                                try:
                                    asset_req = urllib.request.Request(asset_url, headers=headers)
                                    with urllib.request.urlopen(asset_req) as resp_asset, open(local_path, 'wb') as f_out:
                                        f_out.write(resp_asset.read())
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
        except Exception as e:
            print(f"    ⚠️ Erreur connexion Forgejo/Git pour {xml_url}: {e}")

    return assets_collected

# Alias pour compatibilité
fetch_assets_from_url = fetch_repository_assets

def parse_opml_file(opml_path):
    """
    Lit un fichier OPML et extrait la liste des flux/dépôts avec toutes les clés 
    nécessaires pour éviter les KeyError ('xml_url', 'url', etc.).
    """
    feeds = []
    try:
        tree = ET.parse(opml_path)
        root = tree.getroot()
        for outline in root.findall('.//outline'):
            xml_url = outline.get('xmlUrl') or outline.get('url')
            if xml_url:
                title = outline.get('text') or outline.get('title') or "Inconnu"
                description = outline.get('description', '')
                author = outline.get('ownerName', '')
                
                feeds.append({
                    "title": title,
                    "text": title,
                    "xmlUrl": xml_url,
                    "url": xml_url,
                    "description": description,
                    "author": author,
                    "ownerName": author
                })
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture de l'OPML {opml_path}: {e}")
    return feeds

# Alias rétrocompatible
parse_opml_feeds = parse_opml_file
