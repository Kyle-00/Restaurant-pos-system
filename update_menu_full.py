"""
Full menu update – adds new categories, moves items, updates prices/descriptions, deletes old categories.
Run this ONCE to bring your database in line with the new config.py.
WARNING: This will overwrite existing prices and descriptions with the values in config.py.
"""

import sqlite3
from config import DB_PATH, DEFAULT_CATEGORIES, DEFAULT_ITEMS

def get_category_id(cursor, name):
    cursor.execute("SELECT id FROM menu_categories WHERE name = ?", (name,))
    row = cursor.fetchone()
    return row[0] if row else None

def add_or_update_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for name, desc in DEFAULT_CATEGORIES:
        cursor.execute("SELECT id, description FROM menu_categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            if row[1] != desc:
                cursor.execute("UPDATE menu_categories SET description = ? WHERE id = ?", (desc, row[0]))
                print(f"Updated category description: {name}")
        else:
            cursor.execute("INSERT INTO menu_categories (name, description) VALUES (?, ?)", (name, desc))
            print(f"Added category: {name}")
    conn.commit()
    conn.close()

def move_and_update_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Special case: split Cocktails & Mocktails
    old_cat_id = get_category_id(cursor, "Cocktails & Mocktails")
    if old_cat_id:
        cocktails_id = get_category_id(cursor, "Cocktails")
        mocktails_id = get_category_id(cursor, "Mocktails")
        if cocktails_id and mocktails_id:
            cursor.execute("SELECT id, name FROM menu_items WHERE category_id = ?", (old_cat_id,))
            items = cursor.fetchall()
            for item_id, name in items:
                if "virgin" in name.lower() or "mocktail" in name.lower():
                    new_cat_id = mocktails_id
                else:
                    new_cat_id = cocktails_id
                cursor.execute("UPDATE menu_items SET category_id = ? WHERE id = ?", (new_cat_id, item_id))
                print(f"Moved item '{name}' to {'Mocktails' if new_cat_id == mocktails_id else 'Cocktails'}")
            cursor.execute("DELETE FROM menu_categories WHERE id = ?", (old_cat_id,))
            print("Deleted old category: Cocktails & Mocktails")

    # Process all items from DEFAULT_ITEMS: update or insert
    for cat_name, item_name, desc, price, vegan, gluten_free in DEFAULT_ITEMS:
        cat_id = get_category_id(cursor, cat_name)
        if not cat_id:
            print(f"Warning: Category '{cat_name}' not found – skipping item '{item_name}'")
            continue
        cursor.execute("SELECT id, description, price FROM menu_items WHERE name = ? AND category_id = ?", (item_name, cat_id))
        row = cursor.fetchone()
        if row:
            # Update description and price
            update_parts = []
            params = []
            if row[1] != desc:
                update_parts.append("description = ?")
                params.append(desc)
            if row[2] != price:
                update_parts.append("price = ?")
                params.append(price)
            if update_parts:
                params.append(row[0])
                cursor.execute(f"UPDATE menu_items SET {', '.join(update_parts)} WHERE id = ?", params)
                print(f"Updated item: {item_name} (price/description)")
        else:
            # Insert new item
            cursor.execute("""
                INSERT INTO menu_items (category_id, name, description, price, is_vegan, is_gluten_free)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cat_id, item_name, desc, price, int(vegan), int(gluten_free)))
            print(f"Added item: {item_name}")

    conn.commit()
    conn.close()

def delete_empty_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM menu_categories")
    categories = cursor.fetchall()
    for cat_id, name in categories:
        cursor.execute("SELECT COUNT(*) FROM menu_items WHERE category_id = ?", (cat_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("DELETE FROM menu_categories WHERE id = ?", (cat_id,))
            print(f"Deleted empty category: {name}")
    conn.commit()
    conn.close()

def reorder_categories_alphabetically():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM menu_categories ORDER BY name")
    categories = cursor.fetchall()
    for sort_order, (cat_id, name) in enumerate(categories):
        cursor.execute("UPDATE menu_categories SET sort_order = ? WHERE id = ?", (sort_order, cat_id))
    conn.commit()
    conn.close()
    print("Categories reordered alphabetically.")

def run_full_update():
    print("Starting full menu update...")
    add_or_update_categories()
    move_and_update_items()
    delete_empty_categories()
    reorder_categories_alphabetically()
    print("Menu update complete. Please restart the app.")

if __name__ == "__main__":
    run_full_update()