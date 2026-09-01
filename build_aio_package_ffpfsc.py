import os
import sys
import json
import re
import zipfile
import urllib.request
import datetime

FFPFSC_FEED_DIR = os.path.join("feed", "ffpfsc")
FFPFSC_JSON_DIR = os.path.join("json", "ffpfsc")
TMP_BUILD_DIR = "tmp_ffpfsc_aio_build"

if not os.path.exists(FFPFSC_FEED_DIR):
    print(f"⚠️ Le dossier {FFPFSC_FEED_DIR} n'existe pas. Annulation.")
    sys.exit(0)

print("=== Début de la construction de l'archive AIO FFPFSC ===")

os.makedirs(TMP_BUILD_DIR, exist_ok=True)
os.makedirs(FFPFSC_JSON_DIR, exist_ok=True)
date_tag = datetime.datetime.now().strftime("%Y.%m.%d-%H%M")

opml_files = [f for f in os.listdir(FFPFSC_FEED_DIR) if f.endswith('.opml')]

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
urllib.request.install_opener(opener)

all_ffpfsc_list = []

for opml_file in opml_files:
    cat_tech_name = opml_file.replace('.opml', '').lower()
    cat_display_name = cat_tech_name.upper()

    with open(os.path.join(FFPFSC_FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
        content = f.read()

    outlines = re.findall(r'<outline\s+([^>]+)/>', content)
    
    for outline in outlines:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
        title = attrs.get('title', attrs.get('text', 'Inconnu'))
        xml_url = attrs.get('xmlUrl', '').strip()
        author = attrs.get('author', 'Inconnu')
        description = attrs.get('description', f"Fichier FFPFSC {title}")

        if not xml_url:
            continue

        raw_filename = xml_url.split('/')[-1].split('?')[0]
        if not raw_filename.lower().endswith('.ffpfsc'):
            raw_filename = f"{re.sub(r'[^a-zA-Z0-9._-]', '_', title)}.ffpfsc"

        v_match = re.search(r'v(\d+[\.\d+]*)', raw_filename, re.IGNORECASE)
        version = f"v{v_match.group(1)}" if v_match else "v1.0.0"

        target_path = os.path.join(TMP_BUILD_DIR, raw_filename)
        print(f" 📥 Téléchargement de {raw_filename}...")
        
        try:
            urllib.request.urlretrieve(xml_url, target_path)
            all_ffpfsc_list.append({
                "name": title,
                "filename": raw_filename,
                "url": xml_url,
                "description": description,
                "version": version,
                "author": author,
                "category": cat_display_name
            })
        except Exception as e:
            print(f"   ⚠️ Échec du téléchargement pour {raw_filename} : {e}")

# Génération de json/ffpfsc/ffpfsc.json
json_output_path = os.path.join(FFPFSC_JSON_DIR, "ffpfsc.json")
with open(json_output_path, 'w', encoding='utf-8') as fj_out:
    json.dump({"name": "AIO Store FFPFSC", "files": all_ffpfsc_list}, fj_out, indent=2, ensure_ascii=False)

# Inclusion du JSON dans le zip
if os.path.exists(json_output_path):
    with open(json_output_path, 'r', encoding='utf-8') as fj:
        data = json.load(fj)
    with open(os.path.join(TMP_BUILD_DIR, "ffpfsc.json"), 'w', encoding='utf-8') as fj_out:
        json.dump(data, fj_out, indent=2, ensure_ascii=False)

zip_latest_name = "ffpfsc_aio_latest.zip"
zip_tag_name = f"ffpfsc_aio_{date_tag}.zip"

print(f"\n📦 Compression des archives : {zip_latest_name} & {zip_tag_name}...")

for zip_target in [zip_latest_name, zip_tag_name]:
    with zipfile.ZipFile(zip_target, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(TMP_BUILD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, TMP_BUILD_DIR)
                zipf.write(file_path, arcname)

# Nettoyage
for f in os.listdir(TMP_BUILD_DIR):
    try:
        os.remove(os.path.join(TMP_BUILD_DIR, f))
    except Exception:
        pass

try:
    os.rmdir(TMP_BUILD_DIR)
except Exception:
    pass

print("=== Construction AIO FFPFSC terminée avec succès ===")
