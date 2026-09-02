# scripts/generate_web.py

import os
import json
from scripts.config_rules import BASE_URL, PATHS

def build_index_html(data_store):
    """
    Génère index.html avec une interface claire listant le contenu disponible dans le store.
    """
    # Calcul sécurisé basé sur la structure des dictionnaires de catégories retournés par les fetchers
    def count_items(cat_dict):
        if not isinstance(cat_dict, dict):
            return 0
        return sum(len(cat.get("items", [])) for cat in cat_dict.values() if isinstance(cat, dict))

    counts = {
        "payloads": count_items(data_store.get("payloads")),
        "pkg": count_items(data_store.get("pkg")),
        "ffpfsc": count_items(data_store.get("ffpfsc")),
        "apps": count_items(data_store.get("apps"))
    }

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AIO PS5 Store Directory</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #0d1117;
      color: #c9d1d9;
      margin: 0;
      padding: 2rem;
    }}
    .container {{
      max-width: 900px;
      margin: 0 auto;
    }}
    h1 {{
      color: #58a6ff;
      border-bottom: 1px solid #30363d;
      padding-bottom: 0.5rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-top: 1.5rem;
    }}
    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 1.2rem;
      text-align: center;
    }}
    .card h3 {{
      margin-top: 0;
      color: #79c0ff;
    }}
    .card .count {{
      font-size: 2rem;
      font-weight: bold;
      color: #f0f6fc;
    }}
    .card a {{
      display: inline-block;
      margin-top: 0.8rem;
      color: #58a6ff;
      text-decoration: none;
    }}
    .card a:hover {{
      text-decoration: underline;
    }}
    footer {{
      margin-top: 3rem;
      border-top: 1px solid #30363d;
      padding-top: 1rem;
      font-size: 0.85rem;
      color: #8b949e;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 AIO PS5 Store Directory</h1>
    <p>Index dynamique du dépôt synchronisé automatiquement.</p>

    <div class="grid">
      <div class="card">
        <h3>⚡ Payloads</h3>
        <div class="count">{counts['payloads']}</div>
        <a href="json/payloads.json">Voir payloads.json</a>
      </div>
      <div class="card">
        <h3>📦 Packages (PKG)</h3>
        <div class="count">{counts['pkg']}</div>
        <a href="json/pkg.json">Voir pkg.json</a>
      </div>
      <div class="card">
        <h3>📄 FFPFSC</h3>
        <div class="count">{counts['ffpfsc']}</div>
        <a href="json/ffpfsc.json">Voir ffpfsc.json</a>
      </div>
      <div class="card">
        <h3>📱 Applications</h3>
        <div class="count">{counts['apps']}</div>
        <a href="json/apps.json">Voir apps.json</a>
      </div>
    </div>

    <footer>
      Dernière synchronisation automatique | <a href="rss/feed.xml" style="color:#58a6ff;">Flux RSS</a>
    </footer>
  </div>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ Génération de la page Web (index.html) terminée.")
