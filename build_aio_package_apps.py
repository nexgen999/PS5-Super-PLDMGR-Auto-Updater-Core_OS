import os
import sys
import json
import zipfile
import datetime

JSON_DIR = "json"
APPS_JSON = os.path.join(JSON_DIR, "apps.json")
APPS_ROOT = "apps"

def get_latest_apps_paths():
    apps_files = []

    if not os.path.exists(APPS_JSON):
        print(f"⚠️ Le fichier {APPS_JSON} n'existe pas.")
        return apps_files

    try:
        with open(APPS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            apps = data.get("apps", [])

            for item in apps:
                url = item.get("url", "")
                if url:
                    if "/apps/" in url:
                        rel_path = url.split("/apps/")[-1]
                        full_path = os.path.join(APPS_ROOT, os.path.normpath(rel_path))
                    else:
                        full_path = os.path.normpath(url)

                    if os.path.exists(full_path):
                        filename = os.path.basename(full_path)
                        apps_files.append((full_path, filename))
                    else:
                        print(f"⚠️ Fichier App introuvable : {full_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {APPS_JSON} : {e}")
        sys.exit(1)

    return apps_files

def build_aio():
    date_tag = os.environ.get("DATE_TAG")
    if not date_tag:
        now = datetime.datetime.now()
        date_tag = now.strftime("%Y.%m.%d-%H%M")

    zip_timestamp_name = f"PS5_apps_aio_{date_tag}.zip"
    zip_latest_name = "PS5_apps_aio_latest.zip"

    print(f"=== Création du package AIO Apps ({date_tag}) ===")

    apps_to_pack = get_latest_apps_paths()

    if not apps_to_pack:
        print("⚠️ Aucun fichier App trouvé.")
        sys.exit(0)

    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, filename in apps_to_pack:
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name} ({len(apps_to_pack)} fichiers)")

    print("=== Packaging AIO Apps terminé avec succès ===")

if __name__ == "__main__":
    build_aio()
