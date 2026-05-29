import hashlib
import secrets
import sqlite3

from app.models.db import get_connection
from app.models.system import RoleRepository, UserRoleRepository

def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return dk.hex()

class UserRepository:
    @staticmethod
    def create_user(username: str, password: str, role_id: int = None) -> bool:
        salt = secrets.token_bytes(16)
        password_hash = _hash_password(password, salt)

        try:
            with get_connection() as conn:
                cursor = conn.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                            (username, password_hash, salt.hex()))
                user_id = cursor.lastrowid
                if role_id:
                    conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def get_user_by_username(username: str):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()

    @staticmethod
    def verify(username: str, password: str) -> bool:
        user = UserRepository.get_user_by_username(username)
        if not user:
            return False
        salt = bytes.fromhex(user['salt'])
        password_hash = _hash_password(password, salt)
        return password_hash == user['password_hash']

    @staticmethod
    def get_all_users(page: int = 1, page_size: int = 20):
        offset = (page - 1) * page_size
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, username, create_at FROM users ORDER BY id ASC LIMIT ? OFFSET ?",
                (page_size, offset)
            )
            users = [dict(row) for row in cursor.fetchall()]
            
            # 为每个用户添加角色信息
            for user in users:
                roles = RoleRepository.get_user_roles(user['id'])
                if roles:
                    user['role_id'] = roles[0]['id']
                    user['role_name'] = roles[0]['name']
                    user['role_is_system'] = RoleRepository.get_role_by_id(roles[0]['id'])['is_system'] if RoleRepository.get_role_by_id(roles[0]['id']) else 0
                else:
                    user['role_id'] = None
                    user['role_name'] = '未分配'
                    user['role_is_system'] = 0
            
            return users

    @staticmethod
    def get_user_count():
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    @staticmethod
    def delete_user(user_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return True
        except Exception:
            return False

    @staticmethod
    def batch_delete_users(user_ids: list) -> bool:
        try:
            with get_connection() as conn:
                placeholders = ','.join('?' * len(user_ids))
                conn.execute(f"DELETE FROM users WHERE id IN ({placeholders})", user_ids)
            return True
        except Exception:
            return False

    @staticmethod
    def update_user(user_id: int, username: str = None, password: str = None) -> bool:
        try:
            with get_connection() as conn:
                if username:
                    conn.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
                if password:
                    salt = secrets.token_bytes(16)
                    password_hash = _hash_password(password, salt)
                    conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                                (password_hash, salt.hex(), user_id))
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False