"""
Menu categories, items, combos, and customisations.
"""
import sqlite3
from .connection import get_db_connection, get_cursor
from config import DB_PATH
from datetime import datetime


class Database:
    # ---- Categories ----
    @staticmethod
    def get_all_categories():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM menu_categories WHERE is_active = 1 ORDER BY sort_order")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def add_category(name, description="", sort_order=0):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO menu_categories (name, description, sort_order)
                VALUES (?, ?, ?)
            """, (name, description, sort_order))
            return cursor.lastrowid

    @staticmethod
    def update_category(cat_id, name, description, sort_order):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE menu_categories SET name = ?, description = ?, sort_order = ?
                WHERE id = ?
            """, (name, description, sort_order, cat_id))

    # ---- Menu items ----
    @staticmethod
    def get_all_menu_items():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mi.*, mc.name as category_name
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.id
                WHERE mi.is_available = 1 AND mc.is_active = 1
                ORDER BY mc.sort_order, mi.sort_order
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_menu_items_by_category(category_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM menu_items 
                WHERE category_id = ? AND is_available = 1
                ORDER BY sort_order
            """, (category_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def add_menu_item(category_id, name, description, price, is_vegan=0, is_gluten_free=0, prep_time=15):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO menu_items (category_id, name, description, price, is_vegan, is_gluten_free, prep_time_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (category_id, name, description, price, is_vegan, is_gluten_free, prep_time))
            return cursor.lastrowid

    @staticmethod
    def update_menu_item(item_id, **kwargs):
        allowed_fields = ["category_id", "name", "description", "price", 
                         "is_vegan", "is_gluten_free", "is_available", "is_featured", 
                         "prep_time_minutes", "sort_order", "image_path"]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        with get_cursor() as cursor:
            cursor.execute(f"UPDATE menu_items SET {set_clause}, updated_at = ? WHERE id = ?", 
                          (*list(updates.values()), datetime.now(), item_id))
            return cursor.rowcount > 0

    @staticmethod
    def get_menu_item(item_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mi.*, mc.name as category_name
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.id
                WHERE mi.id = ?
            """, (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_menu_item(item_id):
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))

    @staticmethod
    def get_all_menu_items_with_unavailable():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT mi.*, mc.name as category_name
                FROM menu_items mi
                JOIN menu_categories mc ON mi.category_id = mc.id
                WHERE mc.is_active = 1
                ORDER BY mc.sort_order, mi.sort_order
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_menu_items_by_category_unavailable(category_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM menu_items 
                WHERE category_id = ?
                ORDER BY sort_order
            """, (category_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ---- Combo meals ----
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
    def add_combo(name, description, discount_percent, items):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO combo_meals (name, description, discount_percent) VALUES (?, ?, ?)",
            (name, description, discount_percent)
        )
        combo_id = cursor.lastrowid
        for item_id, qty in items:
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

    # ---- Order customisations ----
    @staticmethod
    def get_customisations_for_item(menu_item_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM order_customisations WHERE menu_item_id = ? AND is_active = 1",
            (menu_item_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]