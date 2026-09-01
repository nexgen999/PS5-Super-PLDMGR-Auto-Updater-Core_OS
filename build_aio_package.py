import os
import sys
import json
import zipfile
import datetime

JSON_DIR = "json"
PAYLOADS_JSON = os.path.join(JSON_DIR, "payloads.json")
PAYLOADS_ROOT = "payloads"
RELEASE_NOTES_FILE = "release_notes.md"

def get_latest_elf_paths():
    """
    Extrait les chemins des derniers fichiers ELF/BIN uniquement à partir du fichier payloads.json
    """
    elf_files = []

    if not os.path.exists(PAYLOADS_JSON):
        print(f"❌ Erreur: Le fichier {PAYLOADS_JSON} n'existe pas.")
        sys.exit(1)

    try:
        with open(PAYLOADS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            payloads = data.get("payloads", [])

            for item in payloads:
                url = item.get("url", "")
                if url:
                    # Extraction flexible du chemin relatif quel que soit l'OS
                    if "/payloads/" in url:
                        rel_path = url.split("/payloads/")[-1]
                        full_path = os.path.join(PAYLOADS_ROOT, os.path.normpath(rel_path))
                    else:
                        full_path = os.path.normpath(url)

                    if os.path.exists(full_path):
                        filename = os.path.basename(full_path)
                        elf_files.append((full_path, filename, item.get("name"), item.get("version")))
                    else:
                        print(f"⚠️ Fichier introuvable sur le disque : {full_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {PAYLOADS_JSON} : {e}")
        sys.exit(1)

    return elf_files

def build_aio():
    # Priorité à la variable d'environnement DATE_TAG transmise par GitHub Actions
    date_tag = os.environ.get("DATE_TAG")
    if not date_tag:
        now = datetime.datetime.now()
        date_tag = now.strftime("%Y.%m.%d-%H%M")

    # Nouveaux noms conformes à la nomenclature
    zip_timestamp_name = f"PS5_payloads_aio_{date_tag}.zip"
    zip_latest_name = "PS5_payloads_aio_latest.zip"

    print(f"=== Création du package AIO Payloads ({date_tag}) ===")

    elf_to_pack = get_latest_elf_paths()

    if not elf_to_pack:
        print("⚠️ Aucun fichier ELF/BIN trouvé dans payloads.json.")
        sys.exit(0)

    print(f"📌 {len(elf_to_pack)} payloads uniques (dernières versions) identifiés dans payloads.json.")

    # Création des deux archives ZIP
    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, filename, name, ver in elf_to_pack:
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name} ({len(elf_to_pack)} fichiers)")

    # Génération / Complétion des Release Notes
    with open(RELEASE_NOTES_FILE, "w", encoding="utf-8") as rn:
        rn.write(f"## 🚀 Release AIO Auto-Updated ({date_tag})\n\n")
        rn.write("Cette archive contient **exclusivement la dernière version** de chaque payload répertorié dans `payloads.json`.\n\n")
        rn.write("### 📦 Payloads inclus dans ce package :\n")
        for _, filename, name, ver in sorted(elf_to_pack, key=lambda x: x[1].lower()):
            rn.write(f"- `{filename}` — **{name}** ({ver})\n")

    # Mise à jour de l'environnement GitHub Actions si disponible
    github_env = os.environ.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a', encoding='utf-8') as f:
            f.write(f"AIO_TAG={date_tag}\n")
            f.write(f"ZIP_TIMESTAMP_NAME={zip_timestamp_name}\n")

    print("=== Packaging AIO Payloads terminé avec succès ===")

if __name__ == "__main__":
    build_aio()
