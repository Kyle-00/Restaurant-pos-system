"""
Database Migration System
-------------------------
Manages schema version and applies incremental upgrades.
"""

import sqlite3
from config import DB_PATH

SCHEMA_VERSION_TABLE = "schema_version"
CURRENT_VERSION = 6

def get_schema_version(conn):
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{SCHEMA_VERSION_TABLE}'")
    if not cursor.fetchone():
        return 0
    cursor.execute(f"SELECT version FROM {SCHEMA_VERSION_TABLE} ORDER BY version DESC LIMIT 1")
    row = cursor.fetchone()
    return row[0] if row else 0

def set_schema_version(conn, version):
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {SCHEMA_VERSION_TABLE} (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute(f"INSERT INTO {SCHEMA_VERSION_TABLE} (version) VALUES (?)", (version,))
    conn.commit()

def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    current = get_schema_version(conn)

    if current < 1:
        set_schema_version(conn, 1)
        current = 1

    if current < 2:
        # combo_meals and combo_items
        conn.execute("""
            CREATE TABLE IF NOT EXISTS combo_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                discount_percent REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS combo_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                combo_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (combo_id) REFERENCES combo_meals(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
            )
        """)
        set_schema_version(conn, 2)
        current = 2

    if current < 3:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_customisations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_item_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price_extra REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
            )
        """)
        try:
            conn.execute("ALTER TABLE order_items ADD COLUMN customisations TEXT")
        except sqlite3.OperationalError:
            pass
        set_schema_version(conn, 3)
        current = 3

    if current < 4:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employee_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                shift_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clock_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL CHECK (event_type IN ('clock_in', 'clock_out')),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        set_schema_version(conn, 4)
        current = 4

    if current < 5:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        default_colours = {
            "bg_primary": "#121212",
            "bg_secondary": "#1E1E1E",
            "bg_tertiary": "#282828",
            "bg_input": "#333333",
            "accent_primary": "#1DB954",
            "accent_secondary": "#535353",
            "accent_success": "#1DB954",
            "accent_warning": "#FFB74D",
            "accent_danger": "#E74C3C",
            "accent_gold": "#1DB954",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B3B3B3",
            "text_muted": "#808080",
            "text_on_accent": "#FFFFFF",
        }
        for key, val in default_colours.items():
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
        set_schema_version(conn, 5)
        current = 5

    if current < 6:
        # Add assigned_chef_id to order_items
        try:
            conn.execute("ALTER TABLE order_items ADD COLUMN assigned_chef_id INTEGER REFERENCES users(id)")
            print("Added assigned_chef_id column to order_items")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise
        set_schema_version(conn, 6)
        current = 6

    conn.close()
    print(f"Database schema is at version {current} (current target: {CURRENT_VERSION})")