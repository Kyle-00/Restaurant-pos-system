"""
User authentication and management.
"""
import hashlib
import secrets
from datetime import datetime
from .connection import get_db_connection, get_cursor


class Database:
    @staticmethod
    def authenticate_user(username, password):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, password_hash, salt, full_name, role, is_active
                FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            if row and row["is_active"]:
                password_hash = hashlib.sha256((password + row["salt"]).encode()).hexdigest()
                if password_hash == row["password_hash"]:
                    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), row["id"]))
                    conn.commit()
                    return {
                        "id": row["id"],
                        "username": username,
                        "full_name": row["full_name"],
                        "role": row["role"]
                    }
            return None

    @staticmethod
    def create_user(username, password, full_name, email, role):
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        with get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, full_name, email, role)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, salt, full_name, email, role))
            return cursor.lastrowid

    @staticmethod
    def get_user_by_id(user_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, role, is_active, created_at
                FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_all_users():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, role, is_active, created_at, last_login
                FROM users ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_user(user_id, **kwargs):
        allowed_fields = ["username", "full_name", "email", "role"]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        with get_cursor() as cursor:
            cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", (*list(updates.values()), user_id))
            return cursor.rowcount > 0

    @staticmethod
    def change_password(user_id, new_password):
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
        with get_cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (password_hash, salt, user_id)
            )
            return cursor.rowcount > 0

    @staticmethod
    def delete_user(user_id):
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))