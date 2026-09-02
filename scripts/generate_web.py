# scripts/generate_web.py

import os
import json
from scripts.config_rules import PATHS, BASE_URL

def generate_index_html(data_store):
    """
    Génère la page index.html principale du store à partir des données collectées.
    """
    index_path = "index.html"
    
    # Construction d'un contenu HTML propre et fonctionnel pour le store
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PS5 Super PLDMGR Auto-Updater Store</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
        h2 {{ color: #fb7185; margin-top: 30px; }}
        ul {{ line-height: 1.8; }}
        a {{ color: #38bdf8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .badge {{ background: #334155; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 PS5 Super PLDMGR Store</h1>
        <p>Bienvenue sur l'interface Web officielle et autogénérée de votre store PlayStation 5.</p>
        
        <h2>🔗 Accès Rapides aux Données JSON</h2>
        <ul>
            <li><strong>Payloads :</strong> <a href="{BASE_URL}/json/payloads.json" target="_blank">json/payloads.json</a></li>
            <li><strong>Packages (PKG) :</strong> <a href="{BASE_URL}/json/pkg.json" target="_blank">json/pkg.json</a></li>
            <li><strong>Fichiers FFPFSC :</strong> <a href="{BASE_URL}/json/ffpfsc.json" target="_blank">json/ffpfsc.json</a></li>
            <li><strong>Applications :</strong> <a href="{BASE_URL}/json/apps.json" target="_blank">json/apps.json</a></li>
        </ul>

        <h2>📦 Archives Globales (AIO)</h2>
        <ul>
            <li><a href="{BASE_URL}/archives/PS5_payloads_aio_latest.zip">Pack Payloads AIO (Latest)</a></li>
            <li><a href="{BASE_URL}/archives/PS5_pkg_aio_latest.zip">Pack PKG AIO (Latest)</a></li>
            <li><a href="{BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip">Pack FFPFSC AIO (Latest)</a></li>
            <li><a href="{BASE_URL}/archives/PS5_apps_aio_latest.zip">Pack Apps AIO (Latest)</a></li>
            <li><a href="{BASE_URL}/archives/PS5_ultimate_pack_latest.zip">Ultimate Pack AIO</a></li>
        </ul>
    </div>
</body>
</html>
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("✅ Génération de la page index.html terminée.")

# Alias indispensable pour l'appel depuis update_store.py
build_index_html = generate_index_html
