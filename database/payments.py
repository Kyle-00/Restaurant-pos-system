"""
Payments and payment splits.
"""
from datetime import datetime
from .connection import get_db_connection, get_cursor


class Database:
    @staticmethod
    def process_payment(order_id, employee_id, amount_paid, payment_method, split_type="none",
                       transaction_ref="", notes=""):
        with get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
                order = cursor.fetchone()
                if not order:
                    raise ValueError("Order not found")
                subtotal = order["subtotal"]
                discount = order["discount_amount"]
                tax = order["tax_amount"]
                service = order["service_charge"]
                total = order["total_amount"]
                change_due = max(0, amount_paid - total)
                cursor.execute("""
                    INSERT INTO payments (order_id, employee_id, subtotal, discount_amount, 
                                        tax_amount, service_charge, total_amount, amount_paid,
                                        change_due, payment_method, split_type, transaction_reference, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (order_id, employee_id, subtotal, discount, tax, service, total,
                      amount_paid, change_due, payment_method, split_type, transaction_ref, notes))
                payment_id = cursor.lastrowid
                cursor.execute("""
                    UPDATE orders SET status = 'paid', completed_at = ? WHERE id = ?
                """, (datetime.now(), order_id))
                cursor.execute("""
                    UPDATE tables SET status = 'free', current_order_id = NULL
                    WHERE id = ?
                """, (order["table_id"],))
                conn.commit()
                return payment_id
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def add_payment_split(payment_id, person_name, amount, payment_method):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO payment_splits (payment_id, person_name, amount, payment_method)
                VALUES (?, ?, ?, ?)
            """, (payment_id, person_name, amount, payment_method))
            return cursor.lastrowid

    @staticmethod
    def get_payment_by_order(order_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payments WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_payment_splits(payment_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payment_splits WHERE payment_id = ?", (payment_id,))
            return [dict(row) for row in cursor.fetchall()]