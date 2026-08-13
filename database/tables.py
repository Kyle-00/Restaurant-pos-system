"""
Table management (floor plan).
"""
from .connection import get_db_connection, get_cursor


class Database:
    @staticmethod
    def get_all_tables():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, o.status as order_status, o.id as active_order_id
                FROM tables t
                LEFT JOIN orders o ON t.current_order_id = o.id AND o.status NOT IN ('paid', 'cancelled')
                ORDER BY t.table_number
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_table_by_id(table_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables WHERE id = ?", (table_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_table_status(table_id, status, order_id=None, reservation_name=None, reservation_time=None):
        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE tables 
                SET status = ?, current_order_id = ?, reservation_name = ?, reservation_time = ?
                WHERE id = ?
            """, (status, order_id, reservation_name, reservation_time, table_id))

    @staticmethod
    def add_table(table_number, capacity, position_x=0, position_y=0):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO tables (table_number, capacity, position_x, position_y)
                VALUES (?, ?, ?, ?)
            """, (table_number, capacity, position_x, position_y))
            return cursor.lastrowid