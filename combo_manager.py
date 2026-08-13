"""
Combo Meals Manager
-------------------
Defines and applies bundle discounts when specific items are ordered together.
"""

from database import Database
import sqlite3
from config import DB_PATH

class ComboManager:
    @staticmethod
    def get_all_combos():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM combo_meals WHERE is_active = 1 ORDER BY name")
        combos = [dict(row) for row in cursor.fetchall()]
        for combo in combos:
            cursor.execute("""
                SELECT mi.id, mi.name, ci.quantity
                FROM combo_items ci
                JOIN menu_items mi ON ci.menu_item_id = mi.id
                WHERE ci.combo_id = ?
            """, (combo["id"],))
            combo["items"] = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return combos

    @staticmethod
    def add_combo(name, description, discount_percent, item_ids_with_qty):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO combo_meals (name, description, discount_percent) VALUES (?, ?, ?)",
            (name, description, discount_percent)
        )
        combo_id = cursor.lastrowid
        for item_id, qty in item_ids_with_qty:
            cursor.execute(
                "INSERT INTO combo_items (combo_id, menu_item_id, quantity) VALUES (?, ?, ?)",
                (combo_id, item_id, qty)
            )
        conn.commit()
        conn.close()
        return combo_id

    @staticmethod
    def delete_combo(combo_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM combo_meals WHERE id = ?", (combo_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def find_matching_combo(order_items):
        """
        order_items: list of (menu_item_id, quantity)
        Returns: (combo_id, discount_percent) or (None, 0)
        """
        combos = ComboManager.get_all_combos()
        for combo in combos:
            match = True
            for ci in combo["items"]:
                found = False
                for oi_id, oi_qty in order_items:
                    if oi_id == ci["id"] and oi_qty >= ci["quantity"]:
                        found = True
                        break
                if not found:
                    match = False
                    break
            if match:
                return combo["id"], combo["discount_percent"]
        return None, 0