# build_aio_package_payloads.py
import os
import json
import urllib.request
import zipfile
from datetime import datetime

def build_payloads_package():
    timestamp = datetime.now().strftime("%Y.%m.%d-%H%M")
    os.makedirs("archives", exist_ok=True)
    json_path = "json/payloads.json"
    
    print(f"=== Création du package AIO Payloads ({timestamp}) ===")
    if not os.path.exists(json_path):
        print(f"⚠️ Fichier {json_path} introuvable.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        items = content if isinstance(content, list) else content.get("items", [])
        
        zip_filename = f"archives/PS5_payloads_aio_latest.zip"
        zip_versioned = f"archives/PS5_payloads_aio_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf, \
             zipfile.ZipFile(zip_versioned, 'w', zipfile.ZIP_DEFLATED) as zf_ver:
            for item in items:
                url = item.get("url")
                name = item.get("filename") or (url.split('/')[-1].split('?')[0] if url else "unknown")
                if not url: continue
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        data = resp.read()
                        zf.writestr(name, data)
                        zf_ver.writestr(name, data)
                        print(f"  -> Ajouté : {name}")
                except Exception as e:
                    print(f"  ❌ Erreur {name} : {e}")
        print(f"✅ Archive Payloads créée : {zip_filename}")
    except Exception as e:
        print(f"❌ Erreur lecture {json_path} : {e}")

if __name__ == "__main__":
    build_payloads_package()
