"""
Orders, order items, and kitchen view.
"""
import json
from datetime import datetime
from .connection import get_db_connection, get_cursor
from config import TAX_RATE, SERVICE_CHARGE_RATE


class Database:
    @staticmethod
    def create_order(table_id, employee_id, guest_count=1, special_requests=""):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("""
                    INSERT INTO orders (table_id, employee_id, guest_count, special_requests, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (table_id, employee_id, guest_count, special_requests))
                order_id = cursor.lastrowid
                cursor.execute("""
                    UPDATE tables SET status = 'occupied', current_order_id = ?
                    WHERE id = ?
                """, (order_id, table_id))
                conn.commit()
                return order_id
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def add_order_item(order_id, menu_item_id, quantity, notes="", customisations=None):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT price FROM menu_items WHERE id = ?", (menu_item_id,))
                price = cursor.fetchone()[0]
                extra = 0
                if customisations:
                    for cust in customisations:
                        extra += cust.get("price_extra", 0)
                total = (price + extra) * quantity
                cursor.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price, total_price, notes, customisations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (order_id, menu_item_id, quantity, price + extra, total, notes, json.dumps(customisations) if customisations else None))
                Database._recalculate_order_totals(cursor, order_id)
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def update_order_item_quantity(item_id, new_quantity):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT order_id, unit_price FROM order_items WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                order_id, unit_price = row["order_id"], row["unit_price"]
                new_total = unit_price * new_quantity
                cursor.execute("""
                    UPDATE order_items SET quantity = ?, total_price = ?, updated_at = ?
                    WHERE id = ?
                """, (new_quantity, new_total, datetime.now(), item_id))
                Database._recalculate_order_totals(cursor, order_id)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def remove_order_item(item_id):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT order_id FROM order_items WHERE id = ?", (item_id,))
                order_id = cursor.fetchone()["order_id"]
                cursor.execute("DELETE FROM order_items WHERE id = ?", (item_id,))
                Database._recalculate_order_totals(cursor, order_id)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def _recalculate_order_totals(cursor, order_id):
        cursor.execute("SELECT COALESCE(SUM(total_price), 0) as subtotal FROM order_items WHERE order_id = ? AND status != 'cancelled'", (order_id,))
        subtotal = cursor.fetchone()["subtotal"]
        cursor.execute("SELECT discount_percent FROM orders WHERE id = ?", (order_id,))
        discount_pct = cursor.fetchone()["discount_percent"]
        discount_amount = subtotal * (discount_pct / 100)
        total = subtotal - discount_amount
        vat_amount = total * (TAX_RATE / (1 + TAX_RATE))
        service_charge = 0.0
        cursor.execute("""
            UPDATE orders 
            SET subtotal = ?, discount_amount = ?, tax_amount = ?, service_charge = ?, total_amount = ?, updated_at = ?
            WHERE id = ?
        """, (subtotal, discount_amount, vat_amount, service_charge, total, datetime.now(), order_id))

    @staticmethod
    def get_order_by_id(order_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, t.table_number, u.full_name as employee_name
                FROM orders o
                JOIN tables t ON o.table_id = t.id
                JOIN users u ON o.employee_id = u.id
                WHERE o.id = ?
            """, (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_order_items(order_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.*, mi.name as item_name, mi.is_vegan, mi.is_gluten_free
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                WHERE oi.order_id = ?
                ORDER BY oi.created_at
            """, (order_id,))
            rows = cursor.fetchall()
            items = []
            for row in rows:
                d = dict(row)
                if d.get("customisations"):
                    try:
                        d["customisations"] = json.loads(d["customisations"])
                    except:
                        d["customisations"] = []
                else:
                    d["customisations"] = []
                items.append(d)
            return items

    @staticmethod
    def get_order_items_with_chef(order_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.*, mi.name as item_name, u.full_name as chef_name
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                LEFT JOIN users u ON oi.assigned_chef_id = u.id
                WHERE oi.order_id = ?
                ORDER BY oi.created_at
            """, (order_id,))
            rows = cursor.fetchall()
            items = []
            for row in rows:
                d = dict(row)
                if d.get("customisations"):
                    try:
                        d["customisations"] = json.loads(d["customisations"])
                    except:
                        d["customisations"] = []
                else:
                    d["customisations"] = []
                items.append(d)
            return items

    @staticmethod
    def get_active_orders():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, t.table_number, u.full_name as employee_name
                FROM orders o
                JOIN tables t ON o.table_id = t.id
                JOIN users u ON o.employee_id = u.id
                WHERE o.status NOT IN ('paid', 'cancelled')
                ORDER BY o.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_order_status(order_id, new_status):
        with get_cursor() as cursor:
            completed_at = datetime.now() if new_status in ('paid', 'cancelled') else None
            cursor.execute("""
                UPDATE orders SET status = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
            """, (new_status, datetime.now(), completed_at, order_id))

    @staticmethod
    def update_order_item_status(item_id, new_status):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE order_items SET status = ?, updated_at = ? WHERE id = ?
            """, (new_status, datetime.now(), item_id))

    @staticmethod
    def apply_discount(order_id, discount_percent):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("UPDATE orders SET discount_percent = ? WHERE id = ?", (discount_percent, order_id))
                Database._recalculate_order_totals(cursor, order_id)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def get_kitchen_orders():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.*, o.table_id, t.table_number, o.created_at as order_time,
                       mi.name as item_name, mi.prep_time_minutes, o.special_requests,
                       u.full_name as waiter_name,
                       chef.full_name as assigned_chef_name, oi.assigned_chef_id
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                JOIN tables t ON o.table_id = t.id
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                JOIN users u ON o.employee_id = u.id
                LEFT JOIN users chef ON oi.assigned_chef_id = chef.id
                WHERE oi.status IN ('pending', 'preparing')
                AND o.status NOT IN ('paid', 'cancelled')
                ORDER BY o.created_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def assign_chef_to_order_item(item_id, chef_id):
        with get_cursor() as cursor:
            cursor.execute("UPDATE order_items SET assigned_chef_id = ? WHERE id = ?", (chef_id, item_id))

    @staticmethod
    def get_orders_for_waiter(waiter_id, status_filter=None):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT o.*, t.table_number
                FROM orders o
                JOIN tables t ON o.table_id = t.id
                WHERE o.employee_id = ?
            """
            params = [waiter_id]
            if status_filter:
                query += " AND o.status = ?"
                params.append(status_filter)
            query += " ORDER BY o.created_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]