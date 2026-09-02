# update_store.py
import os
import json
from scripts.config_rules import PATHS
from scripts.fetchers.payloads_fetcher import fetch_payloads_category
from scripts.fetchers.pkg_fetcher import fetch_pkg_category
from scripts.fetchers.ffpfsc_fetcher import fetch_ffpfsc_category
from scripts.fetchers.apps_fetcher import fetch_apps_category
from scripts.generate_json import build_all
from scripts.generate_rss import build_rss_feed
from scripts.generate_readme import build_readme
from scripts.generate_web import build_index_html

def main():
    print("🚀 Démarrage de la mise à jour globale du store PS5...")
    credits_set = set()
    
    # Création des dossiers de base requis par PATHS
    os.makedirs(PATHS["archives_dir"], exist_ok=True)
    os.makedirs(PATHS["json_dir"], exist_ok=True)

    # 1. Scraping et téléchargement par module dédié
    print("🔍 [1/5] Scraping des sources OPML et téléchargement des binaires...")
    payloads_by_cat, payloads_flat = fetch_payloads_category(credits_set)
    pkg_by_cat, pkg_flat = fetch_pkg_category(credits_set)
    ffpfsc_by_cat, ffpfsc_flat = fetch_ffpfsc_category(credits_set)
    apps_by_cat, apps_flat = fetch_apps_category(credits_set)

    # Structure complète par catégories (utilisée par build_readme, build_index_html et generate_json)
    data_store = {
        "payloads": (payloads_by_cat, payloads_flat),
        "pkg": (pkg_by_cat, pkg_flat),
        "ffpfsc": (ffpfsc_by_cat, ffpfsc_flat),
        "apps": (apps_by_cat, apps_flat)
    }

    # Structure par catégories sous forme de dictionnaire simple pour l'UI / README
    data_store_by_cat = {
        "payloads": payloads_by_cat,
        "pkg": pkg_by_cat,
        "ffpfsc": ffpfsc_by_cat,
        "apps": apps_by_cat
    }

    # Structure hybride plate pour les flux RSS
    data_store_flat = {
        "payloads": {"name": "Payloads", "items": payloads_flat},
        "pkg": {"name": "Packages PKG", "items": pkg_flat},
        "ffpfsc": {"name": "Fichiers FFPFSC", "items": ffpfsc_flat},
        "apps": {"name": "Applications", "items": apps_flat}
    }

    # 2. Génération centralisée de tous les fichiers JSON (globaux + sous-catégories)
    print("📦 [2/5] Génération de l'arborescence JSON complète...")
    build_all(data_store)

    # 3. Génération des flux RSS & OPML
    print("📡 [3/5] Génération des flux RSS et OPML...")
    build_rss_feed(data_store_flat)

    # 4. Génération de la page index.html
    print("🌐 [4/5] Génération de la page index.html...")
    build_index_html(data_store_by_cat)

    # 5. Génération README.md et Crédits
    print("📝 [5/5] Mise à jour du README.md et des Crédits...")
    build_readme(credits_set, data_store_by_cat)

    print("✅ Mise à jour du store terminée avec succès !")

if __name__ == "__main__":
    main()
