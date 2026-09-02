# build_aio_ultimate.py
import os
import zipfile
from datetime import datetime

def build_ultimate():
    timestamp = datetime.now().strftime("%Y.%m.%d-%H%M")
    os.makedirs("archives", exist_ok=True)
    
    print("📦 Création du pack ultime (Ultimate Pack AIO)...")
    ultimate_zip = f"archives/PS5_Ultimate_AIO_{timestamp}.zip"
    ultimate_latest = "archives/PS5_Ultimate_AIO_latest.zip"
    
    sub_archives = [
        "archives/PS5_payloads_aio_latest.zip",
        "archives/PS5_pkg_aio_latest.zip",
        "archives/PS5_ffpfsc_aio_latest.zip",
        "archives/PS5_apps_aio_latest.zip"
    ]
    
    with zipfile.ZipFile(ultimate_zip, 'w', zipfile.ZIP_DEFLATED) as uzf, \
         zipfile.ZipFile(ultimate_latest, 'w', zipfile.ZIP_DEFLATED) as uzf_let:
        for z_path in sub_archives:
            if os.path.exists(z_path):
                arcname = os.path.basename(z_path)
                uzf.write(z_path, arcname)
                uzf_let.write(z_path, arcname)
                print(f"  -> Intégré au pack ultime : {arcname}")
            else:
                print(f"  ⚠️ Archive non trouvée (ignorée) : {z_path}")
                
    print("✅ Ultimate Pack AIO créé avec succès.")

if __name__ == "__main__":
    build_ultimate()
