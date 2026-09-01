import os
import sys
import json
import re
import zipfile
import urllib.request
import datetime

PKG_FEED_DIR = "PKGfeed"
PKG_JSON_DIR = "PKGjson"
TMP_BUILD_DIR = "tmp_pkg_aio_build"

if not os.path.exists(PKG_FEED_DIR):
    print(f"⚠️ Le dossier {PKG_FEED_DIR} n'existe pas. Annulation.")
    sys.exit(0)

print("=== Début de la construction de l'archive AIO PKG ===")

os.makedirs(TMP_BUILD_DIR, exist_ok=True)
date_tag = datetime.datetime.now().strftime("%Y.%m.%d-%H%M")

opml_files = [f for f in os.listdir(PKG_FEED_DIR) if f.endswith('.opml')]

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
urllib.request.install_opener(opener)

for opml_file in opml_files:
    with open(os.path.join(PKG_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
        content = f.read()

    outlines = re.findall(r'<outline\s+([^>]+)/>', content)
    
    for outline in outlines:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
        title = attrs.get('title', 'Inconnu')
        xml_url = attrs.get('xmlUrl', '').strip()

        if not xml_url:
            continue

        raw_filename = xml_url.split('/')[-1].split('?')[0]
        if not raw_filename.lower().endswith('.pkg'):
            raw_filename = f"{re.sub(r'[^a-zA-Z0-9._-]', '_', title)}.pkg"

        target_pkg_path = os.path.join(TMP_BUILD_DIR, raw_filename)
        print(f" 📥 Téléchargement de {raw_filename} pour l'archive AIO...")
        
        try:
            urllib.request.urlretrieve(xml_url, target_pkg_path)
        except Exception as e:
            print(f"   ⚠️ Échec de téléchargement pour {raw_filename} : {e}")

# Copie du JSON global pkg dans l'archive AIO s'il existe
global_json_src = os.path.join(PKG_JSON_DIR, "pkg.json")
if os.path.exists(global_json_src):
    try:
        with open(global_json_src, 'r', encoding='utf-8') as fj:
            data = json.load(fj)
        with open(os.path.join(TMP_BUILD_DIR, "pkg.json"), 'w', encoding='utf-8') as fj_out:
            json.dump(data, fj_out, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Échec lors du transfert de pkg.json dans l'archive : {e}")

zip_latest_name = "PS5PKG_aio_latest.zip"
zip_tag_name = f"PS5PKG_aio_{date_tag}.zip"

print(f"\n📦 Compression des archives : {zip_latest_name} & {zip_tag_name}...")

for zip_target in [zip_latest_name, zip_tag_name]:
    with zipfile.ZipFile(zip_target, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(TMP_BUILD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, TMP_BUILD_DIR)
                zipf.write(file_path, arcname)

# Nettoyage complet du dossier temporaire
for f in os.listdir(TMP_BUILD_DIR):
    try:
        os.remove(os.path.join(TMP_BUILD_DIR, f))
    except Exception as e:
        print(f"⚠️ Erreur de suppression de fichier temporaire: {e}")

try:
    os.rmdir(TMP_BUILD_DIR)
except Exception:
    pass

print("=== Construction du package AIO PKG terminée avec succès ===")
