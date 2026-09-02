# scripts/generate_readme.py
import os
from scripts.config_rules import BASE_URL

def build_readme(credits_set, data_store):
    """Génère le README.md complet avec statistiques, listes JSON, flux et crédits."""
    
    by_category_payloads = data_store.get("payloads", {})
    pkg_data = data_store.get("pkg", {})
    ffpfsc_data = data_store.get("ffpfsc", {})
    apps_data = data_store.get("apps", {})

    total_payloads = sum(len(cat.get("items", [])) for cat in by_category_payloads.values()) if isinstance(by_category_payloads, dict) else 0
    total_pkg = sum(len(cat.get("items", [])) for cat in pkg_data.values()) if isinstance(pkg_data, dict) else 0
    total_ffpfsc = sum(len(cat.get("items", [])) for cat in ffpfsc_data.values()) if isinstance(ffpfsc_data, dict) else 0
    total_apps = sum(len(cat.get("items", [])) for cat in apps_data.values()) if isinstance(apps_data, dict) else 0
    total_elements = total_payloads + total_pkg + total_ffpfsc + total_apps

    readme_content = f"""# PS5 Store AIO (All-In-One)

Dépôt automatisé regroupant les derniers payloads, packages PKG, fichiers FFPFSC et applications pour PS5.

🌐 **Site Web Officiel / Hébergement :** [Accéder au site]({BASE_URL})

## 📊 Statistiques, Listes JSON & Flux

| Catégorie | Éléments | Listes JSON | Flux RSS | Flux OPML | Archive AIO (Latest) |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Payloads** | {total_payloads} | [JSON](json/payloads.json) | [RSS](rss/payloads.xml) | [OPML](rss/payloads.opml) | [Télécharger](https://github.com/nexgen999/evox-w2jb/releases/download/latest/payloads_aio_latest.zip) |
| **Packages PKG** | {total_pkg} | [JSON](json/pkg.json) | [RSS](rss/pkg.xml) | [OPML](rss/pkg.opml) | [Télécharger](https://github.com/nexgen999/evox-w2jb/releases/download/latest/pkg_aio_latest.zip) |
| **Fichiers FFPFSC** | {total_ffpfsc} | [JSON](json/ffpfsc.json) | [RSS](rss/ffpfsc.xml) | [OPML](rss/ffpfsc.opml) | [Télécharger](https://github.com/nexgen999/evox-w2jb/releases/download/latest/ffpfsc_aio_latest.zip) |
| **Applications (Apps)** | {total_apps} | [JSON](json/apps.json) | [RSS](rss/apps.xml) | [OPML](rss/apps.opml) | [Télécharger](https://github.com/nexgen999/evox-w2jb/releases/download/latest/apps_aio_latest.zip) |
| **GLOBAL** | **{total_elements}** | [JSON Global](json/list.json) | [RSS Global](rss/feed.xml) | - | [Release Complète Latest](https://github.com/nexgen999/evox-w2jb/releases/tag/latest) |

## 🙏 Remerciements & Crédits
Les sources et auteurs référencés dans ce dépôt :
"""

    for credit in sorted(credits_set):
        readme_content += f"{credit}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
