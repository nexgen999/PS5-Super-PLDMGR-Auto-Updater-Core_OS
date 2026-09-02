# scripts/generate_readme.py

import os
from scripts.config_rules import PATHS, BASE_URL

def generate_readme(credits_list, data_store=None):
    """
    Génère le README.md principal structuré selon les exigences précises du projet.
    Accepte optionnellement data_store pour la compatibilité avec update_store.py.
    """
    readme_path = "README.md"
    
    # Tri et nettoyage des crédits
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

Les flux RSS générés automatiquement permettent de suivre en temps réel les mises à jour des dépôts, des outils et des binaires de la scène PS5. Vous pouvez les intégrer dans n'importe quel lecteur RSS (comme FreshRSS) ou les automatiser via des webhooks (Discord, Telegram, etc.) :
- **Flux RSS Payloads** : `{BASE_URL}/rss/payloads_rss.xml` — _Suivi des nouveautés et mises à jour de payloads (.elf, .bin, .ffpfsc)._
- **Flux RSS Packages (PKG)** : `{BASE_URL}/rss/pkg_rss.xml` — _Suivi des publications de jeux, homebrews et applications au format PKG._
- **Flux RSS Fichiers FFPFSC** : `{BASE_URL}/rss/ffpfsc_rss.xml` — _Suivi des modifications et ajouts de patches de configuration FFPFSC._
- **Flux RSS Applications** : `{BASE_URL}/rss/apps_rss.xml` — _Suivi des mises à jour des outils utilitaires et interfaces de gestion._

---

## 📦 Packs Latest à Télécharger (AIO)

Téléchargez les archives globales prêtes à l'emploi mises à jour à chaque release :
- **Pack Payloads AIO** : [{BASE_URL}/archives/PS5_payloads_aio_latest.zip]({BASE_URL}/archives/PS5_payloads_aio_latest.zip)
- **Pack PKG AIO** : [{BASE_URL}/archives/PS5_pkg_aio_latest.zip]({BASE_URL}/archives/PS5_pkg_aio_latest.zip)
- **Pack FFPFSC AIO** : [{BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip]({BASE_URL}/archives/PS5_ffpfsc_aio_latest.zip)
- **Pack Apps AIO** : [{BASE_URL}/archives/PS5_apps_aio_latest.zip]({BASE_URL}/archives/PS5_apps_aio_latest.zip)
- **Ultimate Pack AIO** : [{BASE_URL}/archives/PS5_ultimate_pack_latest.zip]({BASE_URL}/archives/PS5_ultimate_pack_latest.zip)

---

## 📂 Tableaux par Catégorie et par Section

| Catégorie | Fichier JSON | Flux RSS | Fichiers OPML / Sources |
| :--- | :--- | :--- | :--- |
| **Payloads** | [JSON Global]({BASE_URL}/json/payloads.json) | [RSS]({BASE_URL}/rss/payloads_rss.xml) | [Dossier OPML]({BASE_URL}/feed/payloads/) |
| **Packages (PKG)** | [JSON Global]({BASE_URL}/json/pkg.json) | [RSS]({BASE_URL}/rss/pkg_rss.xml) | [Dossier OPML]({BASE_URL}/feed/pkg/) |
| **Fichiers FFPFSC** | [JSON Global]({BASE_URL}/json/ffpfsc.json) | [RSS]({BASE_URL}/rss/ffpfsc_rss.xml) | [Dossier OPML]({BASE_URL}/feed/ffpfsc/) |
| **Applications** | [JSON Global]({BASE_URL}/json/apps.json) | [RSS]({BASE_URL}/rss/apps_rss.xml) | [Dossier OPML]({BASE_URL}/feed/apps/) |

---

## ☕ Crédits & Sources

Ce projet agrège et structure le travail des développeurs de la scène PS5 :

{credits_content}

---
*Mise à jour automatique assurée par GitHub Actions.*
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Génération du README.md structuré et unifié avec flux RSS détaillée terminée.")

# Alias requis par update_store.py
build_readme = generate_readme
