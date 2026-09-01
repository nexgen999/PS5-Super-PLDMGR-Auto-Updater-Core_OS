import os
import sys
import json
import zipfile
import datetime

JSON_DIR = "json"
PKG_JSON = os.path.join(JSON_DIR, "pkg.json")
PKG_ROOT = "pkg"

def get_latest_pkg_paths():
    pkg_files = []

    if not os.path.exists(PKG_JSON):
        print(f"⚠️ Le fichier {PKG_JSON} n'existe pas.")
        return pkg_files

    try:
        with open(PKG_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            packages = data.get("packages", [])

            for item in packages:
                url = item.get("url", "")
                if url:
                    if "/pkg/" in url:
                        rel_path = url.split("/pkg/")[-1]
                        full_path = os.path.join(PKG_ROOT, os.path.normpath(rel_path))
                    else:
                        full_path = os.path.normpath(url)

                    if os.path.exists(full_path):
                        filename = os.path.basename(full_path)
                        pkg_files.append((full_path, filename))
                    else:
                        print(f"⚠️ Fichier PKG introuvable : {full_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {PKG_JSON} : {e}")
        sys.exit(1)

    return pkg_files

def build_aio():
    date_tag = os.environ.get("DATE_TAG")
    if not date_tag:
        now = datetime.datetime.now()
        date_tag = now.strftime("%Y.%m.%d-%H%M")

    zip_timestamp_name = f"PS5_pkg_aio_{date_tag}.zip"
    zip_latest_name = "PS5_pkg_aio_latest.zip"

    print(f"=== Création du package AIO PKG ({date_tag}) ===")

    pkg_to_pack = get_latest_pkg_paths()

    if not pkg_to_pack:
        print("⚠️ Aucun fichier PKG trouvé.")
        sys.exit(0)

    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, filename in pkg_to_pack:
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name} ({len(pkg_to_pack)} fichiers)")

    print("=== Packaging AIO PKG terminé avec succès ===")

if __name__ == "__main__":
    build_aio()
