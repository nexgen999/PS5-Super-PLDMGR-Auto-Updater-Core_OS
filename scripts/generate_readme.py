# scripts/generate_readme.py

import os
from scripts.config_rules import PATHS, BASE_URL

def generate_readme(credits_list):
    """
    Génère le README.md principal en utilisant strictement les règles et BASE_URL du projet.
    """
    readme_path = "README.md"
    
    # Tri et nettoyage des crédits
    sorted_credits = sorted(list(set(credits_list)))
    credits_content = "\n".join(sorted_credits) if sorted_credits else "_Aucun crédit répertorié._"

    content = f"""# 🚀 PS5 Super PLDMGR Auto-Updater Store

Store automatisé pour PlayStation 5 regroupant les payloads, packages (PKG), fichiers FFPFSC et applications utilitaires.

---

## 📂 Accès Rapide & Liens Directs

| Catégorie | Fichier JSON Global | Flux RSS | Fichier OPML |
| :--- | :--- | :--- | :--- |
| **Payloads** | [JSON]({BASE_URL}/json/payloads.json) | [RSS]({BASE_URL}/rss/payloads_rss.xml) | [OPML]({BASE_URL}/feed/payloads/) |
| **Packages (PKG)** | [JSON]({BASE_URL}/json/pkg.json) | [RSS]({BASE_URL}/rss/pkg_rss.xml) | [OPML]({BASE_URL}/feed/pkg/) |
| **Fichiers FFPFSC** | [JSON]({BASE_URL}/json/ffpfsc.json) | [RSS]({BASE_URL}/rss/ffpfsc_rss.xml) | [OPML]({BASE_URL}/feed/ffpfsc/) |
| **Applications** | [JSON]({BASE_URL}/json/apps.json) | [RSS]({BASE_URL}/rss/apps_rss.xml) | [OPML]({BASE_URL}/feed/apps/) |

---

## 📦 Packs AIO (All-in-One) et Packs Ultimes

Les archives globales prêtes à l'emploi sont générées automatiquement à chaque mise à jour et stockées dans le dossier des archives :
- **Pack Payloads AIO** : `{BASE_URL}/archives/PS5_payloads_aio_latest.zip`
- **Pack PKG AIO** : `{BASE_URL}/archives/PS5_pkg_aio_latest.zip`
- **Pack FFPFSC AIO** : `{BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip`
- **Pack Apps AIO** : `{BASE_URL}/archives/PS5_apps_aio_latest.zip`
- **Ultimate Pack AIO** : `{BASE_URL}/archives/PS5_ultimate_pack_latest.zip` (Regroupe l'ensemble des stores et des binaires)

---

## ☕ Crédits & Sources

Ce projet agrège le travail de divers développeurs et contributeurs de la scène PS5 :

{credits_content}

---
*Mise à jour automatique assurée par GitHub Actions.*
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Génération du README.md terminée avec succès (liens unifiés via config_rules).")
