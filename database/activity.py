"""
Activity log and clock events.
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

    # =====================================================================
    # CLOCK EVENTS (for employee shift management)
    # =====================================================================
    @staticmethod
    def clock_in(user_id, notes=""):
        """Record a clock-in event for a user."""
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO clock_events (user_id, event_type, notes)
                VALUES (?, 'clock_in', ?)
            """, (user_id, notes))

    @staticmethod
    def clock_out(user_id, notes=""):
        """Record a clock-out event for a user."""
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO clock_events (user_id, event_type, notes)
                VALUES (?, 'clock_out', ?)
            """, (user_id, notes))