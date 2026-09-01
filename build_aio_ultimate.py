import os
import zipfile

DATE_TAG = os.environ.get("DATE_TAG", "latest")

zip_latest = "PS5_ultimate_pack_aio_latest.zip"
zip_dated = f"PS5_ultimate_pack_aio_{DATE_TAG}.zip"

archives_to_pack = [
    "PS5_payloads_aio_latest.zip",
    "PS5_pkg_aio_latest.zip",
    "PS5_ffpfsc_aio_latest.zip",
    "PS5_apps_aio_latest.zip"
]

print("📦 Creation du pack ultime (Ultimate Pack AIO)...")

def create_ultimate_zip(output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for archive in archives_to_pack:
            if os.path.exists(archive):
                zip_out.write(archive, os.path.basename(archive))
                print(f"  -> Inclus : {archive}")
            else:
                print(f"  ⚠️ Archive non trouvee (ignoree) : {archive}")

create_ultimate_zip(zip_latest)
if DATE_TAG != "latest":
    create_ultimate_zip(zip_dated)

print("✅ Ultimate Pack AIO cree avec succes.")
