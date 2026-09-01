# scripts/generate_readme.py

import os
from datetime import datetime
from scripts.config_rules import BASE_URL

def build_readme(credits_set, data_store):
    """
    Génère le fichier README.md avec la liste des crédits et le résumé des éléments.
    """
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    counts = {
        "payloads": len(data_store.get("payloads", (None, []))[1]),
        "pkg": len(data_store.get("pkg", (None, []))[1]),
        "ffpfsc": len(data_store.get("ffpfsc", (None, []))[1]),
        "apps": len(data_store.get("apps", (None, []))[1])
    }

    credits_list = "\n".join(sorted(list(credits_set))) if credits_set else "_Aucun crédit spécifié._"

    readme_content = f"""# 🚀 PS5 Super PLDMGR Auto-Updater & Store

Mise à jour automatique des Payloads, PKG, FFPFSC et Applications PS5.

Dernière mise à jour automatique : **{now_str}**

---

### 📊 Contenu du Store

* ⚡ **Payloads** : `{counts['payloads']}` éléments ([json/payloads.json]({BASE_URL}/json/payloads.json))
* 📦 **Packages (PKG)** : `{counts['pkg']}` éléments ([json/pkg.json]({BASE_URL}/json/pkg.json))
* 📄 **FFPFSC** : `{counts['ffpfsc']}` éléments ([json/ffpfsc.json]({BASE_URL}/json/ffpfsc.json))
* 📱 **Applications** : `{counts['apps']}` éléments ([json/apps.json]({BASE_URL}/json/apps.json))

---

### 📡 Flux RSS & Index Web

* 🌐 **Interface Web** : [Voir l'index HTML]({BASE_URL}/index.html)
* 📻 **Flux RSS** : [Accéder à feed.xml]({BASE_URL}/rss/feed.xml)

---

### 👏 Crédits & Projets Sources

{credits_list}
"""

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ Génération du README.md terminée.")
