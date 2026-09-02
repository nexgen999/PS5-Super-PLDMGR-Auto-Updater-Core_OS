# update_store.py
import os
import json
from scripts.fetchers.payloads_fetcher import fetch_payloads_category
from scripts.fetchers.pkg_fetcher import fetch_pkg_category
from scripts.fetchers.ffpfsc_fetcher import fetch_ffpfsc_category
from scripts.fetchers.apps_fetcher import fetch_apps_category
from scripts.generate_rss import build_rss_feed
from scripts.generate_readme import build_readme
from scripts.generate_web import build_index_html  # Import corrigé vers build_index_html

def main():
    print("🚀 Démarrage de la mise à jour globale du store PS5...")
    credits_set = set()

    # 1. Scraping par module dédié
    print("🔍 [1/5] Scraping des sources OPML...")
    payloads_data, payloads_flat = fetch_payloads_category(credits_set)
    pkg_data, pkg_flat = fetch_pkg_category(credits_set)
    ffpfsc_data, ffpfsc_flat = fetch_ffpfsc_category(credits_set)
    apps_data, apps_flat = fetch_apps_category(credits_set)

    data_store = {
        "payloads": payloads_data,
        "pkg": pkg_data,
        "ffpfsc": ffpfsc_data,
        "apps": apps_data
    }

    # 2. Génération des fichiers JSON
    print("📦 [2/5] Génération des fichiers JSON...")
    os.makedirs("json", exist_ok=True)
    
    with open("json/payloads.json", "w", encoding="utf-8") as f:
        json.dump(payloads_flat, f, indent=4, ensure_ascii=False)
    with open("json/pkg.json", "w", encoding="utf-8") as f:
        json.dump(pkg_flat, f, indent=4, ensure_ascii=False)
    with open("json/ffpfsc.json", "w", encoding="utf-8") as f:
        json.dump(ffpfsc_flat, f, indent=4, ensure_ascii=False)
    with open("json/apps.json", "w", encoding="utf-8") as f:
        json.dump(apps_flat, f, indent=4, ensure_ascii=False)
        
    global_flat = payloads_flat + pkg_flat + ffpfsc_flat + apps_flat
    with open("json/list.json", "w", encoding="utf-8") as f:
        json.dump(global_flat, f, indent=4, ensure_ascii=False)

    # 3. Génération des flux RSS & OPML
    print("📡 [3/5] Génération des flux RSS et OPML...")
    build_rss_feed(data_store)

    # 4. Génération de la page index.html
    print("🌐 [4/5] Génération de la page index.html...")
    build_index_html(data_store)

    # 5. Génération README.md
    print("📝 [5/5] Mise à jour du README.md et des Crédits...")
    build_readme(credits_set, data_store)

    print("✅ Mise à jour du store terminée avec succès !")

if __name__ == "__main__":
    main()
