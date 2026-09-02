# scripts/generate_readme.py
import os
from scripts.config_rules import PATHS, BASE_URL

def generate_readme(credits_list, data_store=None):
    readme_path = "README.md"
    
    sorted_credits = sorted(list(set(credits_list)))
    credits_content = "\n".join(sorted_credits) if sorted_credits else "_Aucun crédit répertorié._"

    content = f"""# 🚀 PS5 Super PLDMGR Auto-Updater Core OS

Store automatisé et intelligent pour PlayStation 5 regroupant les payloads, packages (PKG), fichiers FFPFSC et applications utilitaires avec synchronisation continue.

---

## 🌐 Page Web du Store

Accédez à l'interface web interactive générée automatiquement pour explorer le catalogue :
- **Interface Web Principale (index.html)** : [{BASE_URL}/index.html]({BASE_URL}/index.html)

---

## 🔗 Liste des URLs JSON Globales

Retrouvez l'ensemble des points d'accès aux données JSON du store :
- **Payloads Global** : `{BASE_URL}/json/payloads.json`
- **Packages (PKG) Global** : `{BASE_URL}/json/pkg.json`
- **Fichiers FFPFSC Global** : `{BASE_URL}/json/ffpfsc.json`
- **Applications Global** : `{BASE_URL}/json/apps.json`

---

## 📡 Flux RSS & Veille Technologique

Les flux RSS générés automatiquement permettent de suivre en temps réel les mises à jour des dépôts, des outils et des binaires de la scène PS5 :
- **Flux RSS Payloads** : `{BASE_URL}/rss/payloads_rss.xml`
- **Flux RSS Packages (PKG)** : `{BASE_URL}/rss/pkg_rss.xml`
- **Flux RSS Fichiers FFPFSC** : `{BASE_URL}/rss/ffpfsc_rss.xml`
- **Flux RSS Applications** : `{BASE_URL}/rss/apps_rss.xml`

---

## 📦 Packs Latest à Télécharger (AIO)

- **Pack Payloads AIO** : [{BASE_URL}/archives/PS5_payloads_aio_latest.zip]({BASE_URL}/archives/PS5_payloads_aio_latest.zip)
- **Pack PKG AIO** : [{BASE_URL}/archives/PS5_pkg_aio_latest.zip]({BASE_URL}/archives/PS5_pkg_aio_latest.zip)
- **Pack FFPFSC AIO** : [{BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip]({BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip)
- **Pack Apps AIO** : [{BASE_URL}/archives/PS5_apps_aio_latest.zip]({BASE_URL}/archives/PS5_apps_aio_latest.zip)
- **Ultimate Pack AIO** : [{BASE_URL}/archives/PS5_ultimate_pack_latest.zip]({BASE_URL}/archives/PS5_ultimate_pack_latest.zip)

---

## ☕ Crédits & Sources

Ce projet agrège et structure le travail des développeurs de la scène PS5 :

{credits_content}

---
*Mise à jour automatique assurée par GitHub Actions.*
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Génération du README.md terminée avec succès.")

build_readme = generate_readme
