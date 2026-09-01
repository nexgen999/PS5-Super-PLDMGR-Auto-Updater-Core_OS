import os
import sys
import json
import zipfile
import datetime

JSON_DIR = "json"
FFPFSC_JSON = os.path.join(JSON_DIR, "ffpfsc.json")
FFPFSC_ROOT = "ffpfsc"

def get_latest_ffpfsc_paths():
    ffpfsc_files = []

    if not os.path.exists(FFPFSC_JSON):
        print(f"⚠️ Le fichier {FFPFSC_JSON} n'existe pas.")
        return ffpfsc_files

    try:
        with open(FFPFSC_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            files = data.get("files", [])

            for item in files:
                url = item.get("url", "")
                if url:
                    if "/ffpfsc/" in url:
                        rel_path = url.split("/ffpfsc/")[-1]
                        full_path = os.path.join(FFPFSC_ROOT, os.path.normpath(rel_path))
                    else:
                        full_path = os.path.normpath(url)

                    if os.path.exists(full_path):
                        filename = os.path.basename(full_path)
                        ffpfsc_files.append((full_path, filename))
                    else:
                        print(f"⚠️ Fichier FFPFSC introuvable : {full_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {FFPFSC_JSON} : {e}")
        sys.exit(1)

    return ffpfsc_files

def build_aio():
    date_tag = os.environ.get("DATE_TAG")
    if not date_tag:
        now = datetime.datetime.now()
        date_tag = now.strftime("%Y.%m.%d-%H%M")

    zip_timestamp_name = f"PS5_ffpfsc_aio_{date_tag}.zip"
    zip_latest_name = "PS5_ffpfsc_aio_latest.zip"

    print(f"=== Création du package AIO FFPFSC ({date_tag}) ===")

    ffpfsc_to_pack = get_latest_ffpfsc_paths()

    if not ffpfsc_to_pack:
        print("⚠️ Aucun fichier FFPFSC trouvé.")
        sys.exit(0)

    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, filename in ffpfsc_to_pack:
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name} ({len(ffpfsc_to_pack)} fichiers)")

    print("=== Packaging AIO FFPFSC terminé avec succès ===")

if __name__ == "__main__":
    build_aio()
