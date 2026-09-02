# update_store.py
import os
import zipfile
from scripts.config_rules import PATHS
from scripts.fetchers.payloads_fetcher import fetch_payloads_category
from scripts.fetchers.pkg_fetcher import fetch_pkg_category
from scripts.fetchers.ffpfsc_fetcher import fetch_ffpfsc_category
from scripts.fetchers.apps_fetcher import fetch_apps_category
from scripts.generate_json import build_all
from scripts.generate_rss import build_rss_feed
from scripts.generate_readme import build_readme
from scripts.generate_web import build_index_html

def build_aio_archives(payloads_flat, pkg_flat, ffpfsc_flat, apps_flat):
    print("📦 [Bonus] Génération des archives AIO ZIP...")
    archives_dir = PATHS.get("archives_dir", "archives")
    os.makedirs(archives_dir, exist_ok=True)

    def create_zip(zip_name, items):
        zip_path = os.path.join(archives_dir, zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in items:
                file_path = item.get("local_path")
                if file_path and os.path.exists(file_path):
                    zf.write(file_path, arcname=os.path.basename(file_path))
        size_bytes = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
        print(f"   ➔ Archive générée : {zip_path} ({size_bytes} octets)")

    create_zip("PS5_payloads_aio_latest.zip", payloads_flat)
    create_zip("PS5_pkg_aio_latest.zip", pkg_flat)
    create_zip("PS5_ffpfsc_aio_latest.zip", ffpfsc_flat)
    create_zip("PS5_apps_aio_latest.zip", apps_flat)
    create_zip("PS5_ultimate_pack_latest.zip", payloads_flat + pkg_flat + ffpfsc_flat + apps_flat)

def main():
    print("🚀 Démarrage de la mise à jour globale du store PS5...")
    credits_set = set()
    
    os.makedirs(PATHS["archives_dir"], exist_ok=True)
    os.makedirs(PATHS["json_dir"], exist_ok=True)
    os.makedirs(PATHS["payloads_dir"], exist_ok=True)

    print("🔍 [1/5] Scraping des sources OPML et téléchargement des binaires...")
    payloads_by_cat, payloads_flat = fetch_payloads_category(credits_set)
    pkg_by_cat, pkg_flat = fetch_pkg_category(credits_set)
    ffpfsc_by_cat, ffpfsc_flat = fetch_ffpfsc_category(credits_set)
    apps_by_cat, apps_flat = fetch_apps_category(credits_set)

    data_store = {
        "payloads": (payloads_by_cat, payloads_flat),
        "pkg": (pkg_by_cat, pkg_flat),
        "ffpfsc": (ffpfsc_by_cat, ffpfsc_flat),
        "apps": (apps_by_cat, apps_flat)
    }

    data_store_by_cat = {
        "payloads": payloads_by_cat,
        "pkg": pkg_by_cat,
        "ffpfsc": ffpfsc_by_cat,
        "apps": apps_by_cat
    }

    data_store_flat = {
        "payloads": {"name": "Payloads", "items": payloads_flat},
        "pkg": {"name": "Packages PKG", "items": pkg_flat},
        "ffpfsc": {"name": "Fichiers FFPFSC", "items": ffpfsc_flat},
        "apps": {"name": "Applications", "items": apps_flat}
    }

    print("📦 [2/5] Génération de l'arborescence JSON complète...")
    build_all(data_store)

    print("📡 [3/5] Génération des flux RSS et OPML...")
    build_rss_feed(data_store_flat)

    print("🌐 [4/5] Génération de la page index.html...")
    build_index_html(data_store_by_cat)

    print("📝 [5/5] Mise à jour du README.md et des Crédits...")
    build_readme(credits_set, data_store_by_cat)

    build_aio_archives(payloads_flat, pkg_flat, ffpfsc_flat, apps_flat)

    print("✅ Mise à jour du store et des packages terminée avec succès !")

if __name__ == "__main__":
    main()
