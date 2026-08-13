"""
Automated Backup Manager
------------------------
Creates daily backups of the database to a backups/ folder.
"""

import os
import shutil
from datetime import datetime
from config import DB_PATH, BACKUPS_DIR

def ensure_backup_dir():
    if not os.path.exists(BACKUPS_DIR):
        os.makedirs(BACKUPS_DIR)

def create_backup():
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUPS_DIR, f"restaurant_pos_{timestamp}.db")
    shutil.copy2(DB_PATH, backup_file)
    # Keep only last 30 backups
    cleanup_old_backups(30)

def cleanup_old_backups(keep=30):
    files = sorted([f for f in os.listdir(BACKUPS_DIR) if f.startswith("restaurant_pos_") and f.endswith(".db")])
    if len(files) > keep:
        for f in files[:-keep]:
            os.remove(os.path.join(BACKUPS_DIR, f))