"""
Settings Manager
----------------
Handles loading and saving application settings, especially theme colours.
"""

import sqlite3
from config import DB_PATH, Theme as DefaultTheme

class SettingsManager:
    @staticmethod
    def get_setting(key, default=None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    @staticmethod
    def set_setting(key, value):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (key, value)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_theme_colours():
        """Return a dict of all theme colours from settings, falling back to DefaultTheme."""
        colours = {}
        for attr in dir(DefaultTheme):
            if not attr.startswith("_") and isinstance(getattr(DefaultTheme, attr), str):
                val = SettingsManager.get_setting(attr.lower())
                colours[attr] = val if val else getattr(DefaultTheme, attr)
        return colours

    @staticmethod
    def apply_theme_to_root(root):
        """Apply loaded colours to the root window."""
        from config import Theme
        colours = SettingsManager.get_theme_colours()
        for key, val in colours.items():
            if hasattr(Theme, key):
                setattr(Theme, key, val)
        root.configure(bg=Theme.BG_PRIMARY)
        # We'll rely on StyleManager to handle the rest