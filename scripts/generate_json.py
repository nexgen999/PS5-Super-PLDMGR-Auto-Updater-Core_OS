# scripts/generate_json.py

import os
import json
from scripts.config_rules import PATHS

def ensure_directories():
    """Vérifie et crée l'arborescence des dossiers JSON de sortie."""
    os.makedirs(PATHS["json_dir"], exist_ok=True)
    for cat_name, cfg in PATHS["categories"].items():
        os.makedirs(cfg["json"], exist_ok=True)

def build_payloads_json(by_category, all_flat):
    """
    Génère json/payloads/<cat>.json et json/payloads.json.
    Structure 100% conservée : { "name": ..., "payloads": [...] }
    """
    payload_cfg = PATHS["categories"]["payloads"]
    
    # 1. JSONs par sous-catégorie
    for cat_tech, data in by_category.items():
        out_path = os.path.join(payload_cfg["json"], f"{cat_tech}.json")
        payload_data = {
            "name": data["name"],
            "payloads": data["items"]
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(payload_data, f, indent=2, ensure_ascii=False)

    # 2. JSON Global
    glob_path = os.path.join(PATHS["json_dir"], "payloads.json")
    glob_data = {
        "name": "AIO Store Payloads",
        "payloads": all_flat
    }
    with open(glob_path, 'w', encoding='utf-8') as f:
        json.dump(glob_data, f, indent=2, ensure_ascii=False)

def build_generic_json(category_key, list_key_name, global_title, by_category, all_flat):
    """
    Génère les JSONs pour PKG, FFPFSC et APPS.
    Structure conservée :
    - PKG : { "name": ..., "packages": [...] }
    - FFPFSC : { "name": ..., "files": [...] }
    - APPS : { "name": ..., "apps": [...] }
    """
    cat_cfg = PATHS["categories"][category_key]

    # 1. JSONs par sous-catégorie
    for cat_tech, data in by_category.items():
        out_path = os.path.join(cat_cfg["json"], f"{cat_tech}.json")
        cat_data = {
            "name": data["name"],
            list_key_name: data["items"]
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(cat_data, f, indent=2, ensure_ascii=False)

    # 2. JSON Global
    glob_path = os.path.join(PATHS["json_dir"], f"{category_key}.json")
    glob_data = {
        "name": global_title,
        list_key_name: all_flat
    }
    with open(glob_path, 'w', encoding='utf-8') as f:
        json.dump(glob_data, f, indent=2, ensure_ascii=False)

def build_all(data_store):
    """
    Point d'entrée principal pour la génération de tous les JSONs.
    `data_store` est un dictionnaire contenant les données retournées par fetcher.py.
    """
    ensure_directories()

    # Payloads
    if "payloads" in data_store:
        by_cat, flat = data_store["payloads"]
        build_payloads_json(by_cat, flat)

    # PKG
    if "pkg" in data_store:
        by_cat, flat = data_store["pkg"]
        build_generic_json("pkg", "packages", "AIO Store PKG", by_cat, flat)

    # FFPFSC
    if "ffpfsc" in data_store:
        by_cat, flat = data_store["ffpfsc"]
        build_generic_json("ffpfsc", "files", "AIO Store FFPFSC", by_cat, flat)

    # APPS
    if "apps" in data_store:
        by_cat, flat = data_store["apps"]
        build_generic_json("apps", "apps", "AIO Store Apps", by_cat, flat)

    print("✅ Génération des fichiers JSON terminée (structures 100% conformes).")
