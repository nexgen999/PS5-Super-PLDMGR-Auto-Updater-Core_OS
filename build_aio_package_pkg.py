import json
import os
import zipfile

def build_payloads_archive():
    json_path = "json/payloads.json"  # Utilisation du JSON généré par update_store.py
    if not os.path.exists(json_path):
        print(f"❌ Erreur : {json_path} introuvable. Exécute update_store.py d'abord.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("archives", exist_ok=True)
    timestamp = os.popen("date +'%Y.%m.%d-%H%M'").read().strip()
    
    # Création des deux versions : horodatée et latest
    for suffix in [timestamp, "latest"]:
        zip_name = f"archives/PS5_payloads_aio_{suffix}.zip"
        print(f"=== Création du package AIO Payloads ({suffix}) ===")
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Itération sur les éléments listés dans le JSON du store
            items = data if isinstance(data, list) else data.get("items", [])
            for item in items:
                file_path = item.get("path") or item.get("local_path")
                if file_path and os.path.exists(file_path):
                    arcname = os.path.basename(file_path)
                    zf.write(file_path, arcname)
                    print(f"  -> Ajouté : {arcname}")
                
        print(f"✅ Archive Payloads créée : {zip_name}")

if __name__ == "__main__":
    build_payloads_archive()
