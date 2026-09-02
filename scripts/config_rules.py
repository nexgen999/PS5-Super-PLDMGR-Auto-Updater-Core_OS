# scripts/config_rules.py
import os

GITHUB_REPO_ENV = os.environ.get('GITHUB_REPOSITORY', '')
if '/' in GITHUB_REPO_ENV:
    GITHUB_USER, REPO_NAME = GITHUB_REPO_ENV.split('/', 1)
else:
    GITHUB_USER, REPO_NAME = 'nexgen999', 'PS5-Super-PLDMGR-Auto-Updater-Core_OS' 
BASE_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}"

PATHS = {
    "feed_dir": "feed",
    "json_dir": "json",
    "payloads_dir": "payloads",
    "rss_dir": "rss",
    "archives_dir": "archives",
    "categories": {
        "payloads": {"feed": "feed/payloads", "json": "json/payloads", "root": "payloads"},
        "pkg": {"feed": "feed/pkg", "json": "json/pkg"},
        "ffpfsc": {"feed": "feed/ffpfsc", "json": "json/ffpfsc"},
        "apps": {"feed": "feed/apps", "json": "json/apps"},
    }
}

REPO_RULES = {
    "extract_zip_repos": [
        "poords4", 
        "fan_target", 
        "shadowmountplus", 
        "instalador-host-psm-poop2jb"
    ],
    "strict_clean_repos": [
        "ps5-payload-dev/websrv", 
        "phantomptr/ps5upload", 
        "boazvdwansem/ps5-debugger"
    ],
    "keep_original_filename_repos": [
        "instalador-host-psm-poop2jb", 
        "psm", 
        "poords4"
    ]
}

DISALLOWED_EXTENSIONS = ('.dmg', '.exe', '.appimage', '.msi', '.txt')
