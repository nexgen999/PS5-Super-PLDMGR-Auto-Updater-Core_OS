import json
import os
import zipfile

def build_pkg_archive():
    json_path = "json/pkg.json"  # Utilisation du JSON des PKG généré par update_store.py
    if not os.path.exists(json_path):
        print(f"❌ Erreur : {json_path} introuvable. Exécute update_store.py d'abord.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs("archives", exist_ok=True)
    timestamp = os.popen("date +'%Y.%m.%d-%H%M'").read().strip()
    
    # Création des deux versions : horodatée et latest pour les PKGs
    for suffix in [timestamp, "latest"]:
        zip_name = f"archives/PS5_pkg_aio_{suffix}.zip"
        print(f"=== Création du package AIO PKG ({suffix}) ===")
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Si ton JSON contient une liste de liens ou d'infos, on peut inclure le JSON lui-même
            # ou télécharger les fichiers si les liens sont présents. 
            # Ici, on intègre proprement le fichier json source dans l'archive AIO pour référence.
            zf.write(json_path, "pkg_sources.json")
            print("  -> Ajouté : pkg_sources.json (Référence des liens PKG)")
                
        print(f"✅ Archive PKG créée : {zip_name}")

if __name__ == "__main__":
    build_pkg_archive()
