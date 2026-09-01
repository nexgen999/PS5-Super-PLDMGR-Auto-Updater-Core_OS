# update_store.py

import os
import sys
from scripts import fetcher, generate_json, generate_rss, generate_web, generate_readme

def main():
    print("🚀 Démarrage de la mise à jour globale du store PS5...\n")
    
    # Ensemble global pour accumuler les crédits auteurs
    credits_set = set()

    # 1. Scraping et récupération de toutes les catégories
    print("🔍 [1/5] Scraping des sources OPML...")
    data_store = {}
    
    print("   -> Traitement des Payloads...")
    data_store["payloads"] = fetcher.fetch_payloads(credits_set)
    
    print("   -> Traitement des PKG...")
    data_store["pkg"] = fetcher.fetch_generic_category("pkg", "packages", ".pkg", credits_set)
    
    print("   -> Traitement des FFPFSC...")
    data_store["ffpfsc"] = fetcher.fetch_generic_category("ffpfsc", "files", ".bin", credits_set)
    
    print("   -> Traitement des Applications...")
    data_store["apps"] = fetcher.fetch_generic_category("apps", "apps", ".pkg", credits_set)

    # 2. Génération des fichiers JSON (Structure 100% rétrocompatible)
    print("\n📄 [2/5] Génération des fichiers JSON...")
    generate_json.build_all(data_store)

    # 3. Génération du flux RSS XML
    print("\n📡 [3/5] Génération du flux RSS...")
    generate_rss.build_rss_feed(data_store)

    # 4. Génération du tableau de bord Web (index.html)
    print("\n🌐 [4/5] Génération de la page index.html...")
    generate_web.build_index_html(data_store)

    # 5. Génération de la documentation README.md
    print("\n📝 [5/5] Génération du README.md et des Crédits...")
    generate_readme.build_readme(credits_set, data_store)

    print("\n🎉 Processus terminé avec succès !")

if __name__ == "__main__":
    main()
