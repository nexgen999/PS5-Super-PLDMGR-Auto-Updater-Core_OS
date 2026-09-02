# scripts/fetchers/utils.py
import os
import re
import html
import json
import urllib.request
import subprocess

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

def fetch_assets_from_url(xml_url, title, description, author, allowed_extensions):
    """Récupère les assets compatibles pour une URL donnée (Fixe, GitHub, GitLab, Gitea, Forgejo)."""
    assets_collected = []
    clean_url = xml_url.split('?')[0].lower()
    version = "v1.0.0"

    # 1. URL Fixe directe
    if clean_url.endswith(allowed_extensions):
        f_name = xml_url.split('/')[-1].split('?')[0]
        assets_collected.append({
            "name": title,
            "filename": f_name,
            "url": xml_url,
            "description": description or f"Fichier {title}",
            "version": version,
            "author": author
        })
        return assets_collected

    # 2. GitHub Repository
    if "github.com" in xml_url:
        repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
        if repo_match:
            repo = repo_match.group(1).rstrip('/')
            try:
                res = subprocess.check_output(f"gh release view --repo {repo} --json assets,tagName", shell=True).decode()
                data = json.loads(res)
                version = data.get('tagName', 'v1.0.0')
                for asset in data.get('assets', []):
                    if asset.get('name', '').lower().endswith(allowed_extensions):
                        assets_collected.append({
                            "name": f"{title} ({asset.get('name')})" if len(data.get('assets', [])) > 1 else title,
                            "filename": asset.get('name'),
                            "url": asset.get('url'),
                            "description": description or f"Asset {asset.get('name')} pour {title}",
                            "version": version,
                            "author": author
                        })
            except: pass

    # 3. GitLab / Gitea / Forgejo / Instances autohébergées (ex: git.etawen.dev, codeberg.org, etc.)
    elif any(domain in xml_url for domain in ["git.", "codeberg.org", "gitlab.com", "gitea"]):
        try:
            api_match = re.search(r'(https?://[^/]+)/([^/]+/[^/]+)', xml_url)
            if api_match:
                base_domain = api_match.group(1)
                repo_path = api_match.group(2).rstrip('/')
                
                # Détection Gitea/Forgejo vs GitLab
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
                            if asset.get('name', '').lower().endswith(allowed_extensions):
                                assets_collected.append({
                                    "name": title,
                                    "filename": asset.get('name'),
                                    "url": asset.get('browser_download_url', asset.get('url')),
                                    "description": description or f"Asset {asset.get('name')}",
                                    "version": version,
                                    "author": author
                                })
        except: pass

    return assets_collected
