"""
Activity log.
"""
from .connection import get_db_connection, get_cursor


class Database:
    @staticmethod
    def log_activity(user_id, action, table_name=None, record_id=None, old_value=None, new_value=None):
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, table_name, record_id, old_value, new_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, table_name, record_id, old_value, new_value))

    @staticmethod
    def get_recent_activity(limit=50):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT al.*, u.full_name as user_name
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.id
                ORDER BY al.created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]