"""
Update menu from config.py – adds new categories/items and updates existing ones.
WARNING: This will overwrite existing item prices and descriptions.
"""

import sqlite3
from config import DB_PATH, DEFAULT_CATEGORIES, DEFAULT_ITEMS

def update_menu(confirm=True):
    if confirm:
        response = input("This will update existing item prices and descriptions. Continue? (y/n): ")
        if response.lower() != 'y':
            print("Update cancelled.")
            return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update categories (description)
    for name, desc in DEFAULT_CATEGORIES:
        cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE menu_categories SET description = ? WHERE name = ?", (desc, name))
            print(f"Updated category: {name}")
        else:
            cursor.execute("INSERT INTO menu_categories (name, description) VALUES (?, ?)", (name, desc))
            print(f"Added category: {name}")

    # Update or insert items
    for cat_name, item_name, desc, price, vegan, gluten_free in DEFAULT_ITEMS:
        cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (cat_name,))
        row = cursor.fetchone()
        if not row:
            print(f"Warning: Category '{cat_name}' not found – skipping item '{item_name}'")
            continue
        cat_id = row[0]
        cursor.execute("SELECT id FROM menu_items WHERE name = ? AND category_id = ?", (item_name, cat_id))
        existing = cursor.fetchone()
        if existing:
            # Update existing item
            cursor.execute("""
                UPDATE menu_items 
                SET description = ?, price = ?, is_vegan = ?, is_gluten_free = ?
                WHERE id = ?
            """, (desc, price, int(vegan), int(gluten_free), existing[0]))
            print(f"Updated item: {item_name}")
        else:
            # Insert new item
            cursor.execute("""
                INSERT INTO menu_items (category_id, name, description, price, is_vegan, is_gluten_free)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cat_id, item_name, desc, price, int(vegan), int(gluten_free)))
            print(f"Added item: {item_name}")

    conn.commit()
    conn.close()
    print("Menu update complete.")

if __name__ == "__main__":
    update_menu()