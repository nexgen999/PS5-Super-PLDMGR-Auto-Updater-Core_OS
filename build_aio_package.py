# build_aio_package.py
import os
import json
import urllib.request
import zipfile
from datetime import datetime

def build_packages():
    timestamp = datetime.now().strftime("%Y.%m.%d-%H%M")
    os.makedirs("archives", exist_ok=True)
    
    categories = ["payloads", "pkg", "ffpfsc", "apps"]
    archive_paths = []

    for cat in categories:
        json_path = f"json/{cat}.json"
        print(f"=== Création du package AIO {cat.capitalize()} ({timestamp}) ===")
        
        if not os.path.exists(json_path):
            print(f"⚠️ Fichier {json_path} introuvable.")
            continue
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            # Gère aussi bien une liste directe qu'un dictionnaire avec 'items'
            items = content if isinstance(content, list) else content.get("items", [])
            
            if not items:
                print(f"⚠️ Aucun élément trouvé dans {json_path}")
                continue

            zip_filename = f"archives/PS5_{cat}_aio_latest.zip"
            zip_versioned = f"archives/PS5_{cat}_aio_{timestamp}.zip"
            
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf, \
                 zipfile.ZipFile(zip_versioned, 'w', zipfile.ZIP_DEFLATED) as zf_ver:
                
                for item in items:
                    url = item.get("url")
                    name = item.get("filename") or (url.split('/')[-1].split('?')[0] if url else "unknown")
                    if not url:
                        continue
                    
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=15) as response:
                            file_data = response.read()
                            zf.writestr(name, file_data)
                            zf_ver.writestr(name, file_data)
                            print(écrit := f"  -> Ajouté : {name}")
                    except Exception as e:
                        print(f"  ❌ Erreur de téléchargement pour {name} : {e}")
                        
            archive_paths.append(zip_filename)
            print(f"✅ Archive créée : {zip_filename}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de {json_path} : {e}")

    # Création du pack ultime regroupant toutes les archives
    print("📦 Création du pack ultime (Ultimate Pack AIO)...")
    ultimate_zip = f"archives/PS5_Ultimate_AIO_{timestamp}.zip"
    ultimate_latest = "archives/PS5_Ultimate_AIO_latest.zip"
    
    with zipfile.ZipFile(ultimate_zip, 'w', zipfile.ZIP_DEFLATED) as uzf, \
         zipfile.ZipFile(ultimate_latest, 'w', zipfile.ZIP_DEFLATED) as uzf_let:
        for z_path in archive_paths:
            if os.path.exists(z_path):
                arcname = os.path.basename(z_path)
                uzf.write(z_path, arcname)
                uzf_let.write(z_path, arcname)
                print(f"  -> Intégré au pack ultime : {arcname}")
            else:
                print(f"  ⚠️ Archive non trouvée (ignorée) : {z_path}")
                
    print("✅ Ultimate Pack AIO créé avec succès.")

if __name__ == "__main__":
    build_packages()
