import sqlite3
from app.models.db import get_connection

class MenuRepository:
    @staticmethod
    def get_all_menus():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, parent_id, name, url, icon, order_num, create_at FROM menus ORDER BY order_num ASC, id ASC"
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_menu_tree():
        menus = MenuRepository.get_all_menus()
        tree = []
        menu_map = {}
        
        for menu in menus:
            menu['children'] = []
            menu_map[menu['id']] = menu
        
        for menu in menus:
            if menu['parent_id'] == 0:
                tree.append(menu)
            else:
                parent = menu_map.get(menu['parent_id'])
                if parent:
                    parent['children'].append(menu)
        
        return tree

    @staticmethod
    def create_menu(name: str, url: str = None, icon: str = None, parent_id: int = 0, order_num: int = 0) -> int:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO menus (name, url, icon, parent_id, order_num) VALUES (?, ?, ?, ?, ?)",
                (name, url, icon, parent_id, order_num)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update_menu(menu_id: int, name: str = None, url: str = None, icon: str = None, order_num: int = None) -> bool:
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if url is not None:
            updates.append("url = ?")
            params.append(url)
        if icon is not None:
            updates.append("icon = ?")
            params.append(icon)
        if order_num is not None:
            updates.append("order_num = ?")
            params.append(order_num)
        
        if not updates:
            return False
        
        params.append(menu_id)
        with get_connection() as conn:
            conn.execute(f"UPDATE menus SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
            return True

    @staticmethod
    def delete_menu(menu_id: int) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM menus WHERE id = ? OR parent_id = ?", (menu_id, menu_id))
            conn.commit()
            return True

    @staticmethod
    def get_role_menus(role_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT menu_id FROM role_menus WHERE role_id = ?", (role_id,)
            )
            return [row['menu_id'] for row in cursor.fetchall()]

    @staticmethod
    def set_role_menus(role_id: int, menu_ids: list) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM role_menus WHERE role_id = ?", (role_id,))
            for menu_id in menu_ids:
                conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", (role_id, menu_id))
            conn.commit()
            return True


class RoleRepository:
    @staticmethod
    def get_all_roles():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, code, is_system, create_at FROM roles ORDER BY is_system DESC, id ASC"
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_role_by_id(role_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, code, is_system, create_at FROM roles WHERE id = ?", (role_id,)
            )
            return cursor.fetchone()

    @staticmethod
    def create_role(name: str, code: str) -> int:
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO roles (name, code, is_system) VALUES (?, ?, 0)",
                    (name, code)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1

    @staticmethod
    def update_role(role_id: int, name: str = None, code: str = None) -> bool:
        try:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if code is not None:
                updates.append("code = ?")
                params.append(code)
            
            if not updates:
                return False
            
            params.append(role_id)
            with get_connection() as conn:
                conn.execute(f"UPDATE roles SET {', '.join(updates)} WHERE id = ? AND is_system = 0", params)
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def delete_role(role_id: int) -> bool:
        role = RoleRepository.get_role_by_id(role_id)
        if not role or role['is_system'] == 1:
            return False
        
        with get_connection() as conn:
            conn.execute("DELETE FROM roles WHERE id = ? AND is_system = 0", (role_id,))
            conn.execute("DELETE FROM role_menus WHERE role_id = ?", (role_id,))
            conn.execute("DELETE FROM user_roles WHERE role_id = ?", (role_id,))
            conn.commit()
            return True

    @staticmethod
    def get_user_roles(user_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                """SELECT r.id, r.name, r.code 
                   FROM roles r 
                   INNER JOIN user_roles ur ON r.id = ur.role_id 
                   WHERE ur.user_id = ?""", (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]


class UserRoleRepository:
    @staticmethod
    def set_user_roles(user_id: int, role_ids: list) -> bool:
        with get_connection() as conn:
            conn.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
            for role_id in role_ids:
                conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
            conn.commit()
            return True

    @staticmethod
    def get_role_users(role_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                """SELECT u.id, u.username, u.create_at 
                   FROM users u 
                   INNER JOIN user_roles ur ON u.id = ur.user_id 
                   WHERE ur.role_id = ?""", (role_id,)
            )
            return [dict(row) for row in cursor.fetchall()]


class ModelRepository:
    @staticmethod
    def get_all_models():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, model_name, api_key, base_url, is_default, total_tokens, create_at FROM ai_models ORDER BY is_default DESC, id DESC"
            )
            models = [dict(row) for row in cursor.fetchall()]
            for m in models:
                m['is_default'] = m['is_default'] == 1
            return models

    @staticmethod
    def get_model_by_id(model_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, model_name, api_key, base_url, is_default, total_tokens, create_at FROM ai_models WHERE id = ?",
                (model_id,)
            )
            model = cursor.fetchone()
            if model:
                model = dict(model)
                model['is_default'] = model['is_default'] == 1
            return model

    @staticmethod
    def get_default_model():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, model_name, api_key, base_url, is_default, total_tokens, create_at FROM ai_models WHERE is_default = 1"
            )
            model = cursor.fetchone()
            if model:
                model = dict(model)
                model['is_default'] = True
            return model

    @staticmethod
    def create_model(name: str, model_name: str, api_key: str, base_url: str, is_default: bool = False) -> int:
        try:
            with get_connection() as conn:
                if is_default:
                    conn.execute("UPDATE ai_models SET is_default = 0")
                
                cursor = conn.execute(
                    "INSERT INTO ai_models (name, model_name, api_key, base_url, is_default, total_tokens) VALUES (?, ?, ?, ?, ?, 0)",
                    (name, model_name, api_key, base_url, 1 if is_default else 0)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建模型失败: {e}")
            return -1

    @staticmethod
    def update_model(model_id: int, name: str = None, model_name: str = None, api_key: str = None, base_url: str = None, is_default: bool = None) -> bool:
        try:
            with get_connection() as conn:
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                if model_name is not None:
                    updates.append("model_name = ?")
                    params.append(model_name)
                if api_key is not None:
                    updates.append("api_key = ?")
                    params.append(api_key)
                if base_url is not None:
                    updates.append("base_url = ?")
                    params.append(base_url)
                if is_default is not None:
                    if is_default:
                        conn.execute("UPDATE ai_models SET is_default = 0")
                    updates.append("is_default = ?")
                    params.append(1 if is_default else 0)
                
                if not updates:
                    return False
                
                params.append(model_id)
                conn.execute(f"UPDATE ai_models SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
                return True
        except Exception as e:
            print(f"更新模型失败: {e}")
            return False

    @staticmethod
    def delete_model(model_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM ai_models WHERE id = ?", (model_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除模型失败: {e}")
            return False

    @staticmethod
    def set_default_model(model_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("UPDATE ai_models SET is_default = 0")
                conn.execute("UPDATE ai_models SET is_default = 1 WHERE id = ?", (model_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"设置默认模型失败: {e}")
            return False

    @staticmethod
    def update_tokens(model_id: int, tokens: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("UPDATE ai_models SET total_tokens = total_tokens + ? WHERE id = ?", (tokens, model_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"更新token失败: {e}")
            return False


class SpySourceRepository:
    @staticmethod
    def get_all_sources():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, entry_url, request_headers, is_active, create_at FROM spy_sources ORDER BY id"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_active_sources():
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, entry_url, request_headers, is_active, create_at FROM spy_sources WHERE is_active = 1 ORDER BY id"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_source_by_id(source_id: int):
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, name, entry_url, request_headers, is_active, create_at FROM spy_sources WHERE id = ?",
                (source_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create_source(name: str, entry_url: str, request_headers: str) -> int:
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO spy_sources (name, entry_url, request_headers, is_active) VALUES (?, ?, ?, 1)",
                    (name, entry_url, request_headers)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建采集源失败: {e}")
            return -1
    
    @staticmethod
    def update_source(source_id: int, name: str = None, entry_url: str = None, request_headers: str = None, is_active: bool = None) -> bool:
        try:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if entry_url is not None:
                updates.append("entry_url = ?")
                params.append(entry_url)
            if request_headers is not None:
                updates.append("request_headers = ?")
                params.append(request_headers)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if not updates:
                return False
            
            params.append(source_id)
            with get_connection() as conn:
                conn.execute(f"UPDATE spy_sources SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
                return True
        except Exception as e:
            print(f"更新采集源失败: {e}")
            return False
    
    @staticmethod
    def delete_source(source_id: int) -> bool:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM spy_sources WHERE id = ?", (source_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除采集源失败: {e}")
            return False


class SpyDataRepository:
    @staticmethod
    def get_paginated_data(page: int = 1, page_size: int = 20):
        offset = (page - 1) * page_size
        with get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT sd.*, ss.name as source_name 
                FROM spy_data sd 
                LEFT JOIN spy_sources ss ON sd.source_id = ss.id 
                ORDER BY sd.id DESC 
                LIMIT ? OFFSET ?
                """,
                (page_size, offset)
            )
            data = [dict(row) for row in cursor.fetchall()]
            
            cursor_total = conn.execute("SELECT COUNT(*) as total FROM spy_data")
            total = cursor_total.fetchone()["total"]
            
            return data, total
    
    @staticmethod
    def insert_data(source_id: int, keyword: str, title: str, url: str, summary: str = None):
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO spy_data (source_id, keyword, title, url, summary) VALUES (?, ?, ?, ?, ?)",
                    (source_id, keyword, title, url, summary)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"插入数据失败: {e}")
            return False
    
    @staticmethod
    def delete_data(data_id: int):
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM spy_data WHERE id = ?", (data_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除数据失败: {e}")
            return False
    
    @staticmethod
    def batch_delete_data(data_ids: list):
        if not data_ids:
            return True
        try:
            with get_connection() as conn:
                placeholders = ", ".join("?" for _ in data_ids)
                conn.execute(f"DELETE FROM spy_data WHERE id IN ({placeholders})", data_ids)
                conn.commit()
                return True
        except Exception as e:
            print(f"批量删除数据失败: {e}")
            return False


# --------------------------
# 任务六：请求伪造与安全防护
# --------------------------
class ForgeryTemplateRepository:
    @staticmethod
    def get_all_templates():
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM forgery_templates ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_template_by_id(template_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM forgery_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create_template(name: str, attack_type: str, description: str = None, 
                       headers: str = None, params: str = None, payloads: str = None):
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO forgery_templates (name, attack_type, description, headers, params, payloads) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, attack_type, description, headers, params, payloads)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建模板失败: {e}")
            return -1
    
    @staticmethod
    def update_template(template_id: int, name: str = None, attack_type: str = None, 
                       description: str = None, headers: str = None, params: str = None, 
                       payloads: str = None, is_active: bool = None):
        try:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if attack_type is not None:
                updates.append("attack_type = ?")
                params.append(attack_type)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if headers is not None:
                updates.append("headers = ?")
                params.append(headers)
            if payloads is not None:
                updates.append("payloads = ?")
                params.append(payloads)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if not updates:
                return False
            
            params.append(template_id)
            with get_connection() as conn:
                conn.execute(f"UPDATE forgery_templates SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
                return True
        except Exception as e:
            print(f"更新模板失败: {e}")
            return False
    
    @staticmethod
    def delete_template(template_id: int):
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM forgery_templates WHERE id = ?", (template_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False


class AttackLogRepository:
    @staticmethod
    def get_paginated_logs(page: int = 1, page_size: int = 20):
        offset = (page - 1) * page_size
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM attack_logs ORDER BY id DESC LIMIT ? OFFSET ?",
                (page_size, offset)
            )
            data = [dict(row) for row in cursor.fetchall()]
            
            cursor_total = conn.execute("SELECT COUNT(*) as total FROM attack_logs")
            total = cursor_total.fetchone()["total"]
            return data, total
    
    @staticmethod
    def create_log(source_id: int, template_id: int, attack_type: str, target_url: str,
                  request_data: str, response_data: str, status_code: int, is_blocked: bool):
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO attack_logs (source_id, template_id, attack_type, target_url, request_data, response_data, status_code, is_blocked) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (source_id, template_id, attack_type, target_url, request_data, response_data, status_code, 1 if is_blocked else 0)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建日志失败: {e}")
            return -1


# --------------------------
# 任务七：多类型存储配置
# --------------------------
class StorageConfigRepository:
    @staticmethod
    def get_all_configs():
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM storage_configs ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_config_by_id(config_id: int):
        with get_connection() as conn:
            cursor = conn.execute("SELECT * FROM storage_configs WHERE id = ?", (config_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create_config(name: str, storage_type: str, connection_string: str = None, config: str = None):
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO storage_configs (name, storage_type, connection_string, config) VALUES (?, ?, ?, ?)",
                    (name, storage_type, connection_string, config)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"创建存储配置失败: {e}")
            return -1
    
    @staticmethod
    def update_config(config_id: int, name: str = None, storage_type: str = None,
                     connection_string: str = None, config: str = None, is_active: bool = None,
                     last_test_at: str = None):
        try:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if storage_type is not None:
                updates.append("storage_type = ?")
                params.append(storage_type)
            if connection_string is not None:
                updates.append("connection_string = ?")
                params.append(connection_string)
            if config is not None:
                updates.append("config = ?")
                params.append(config)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            if last_test_at is not None:
                updates.append("last_test_at = ?")
                params.append(last_test_at)
            
            if not updates:
                return False
            
            params.append(config_id)
            with get_connection() as conn:
                conn.execute(f"UPDATE storage_configs SET {', '.join(updates)} WHERE id = ?", params)
                conn.commit()
                return True
        except Exception as e:
            print(f"更新存储配置失败: {e}")
            return False
    
    @staticmethod
    def delete_config(config_id: int):
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM storage_configs WHERE id = ?", (config_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除存储配置失败: {e}")
            return False


# 更新数据源，添加安全防护开关支持
class SpySourceRepositoryDefense(SpySourceRepository):
    @staticmethod
    def update_defense(source_id: int, enable_defense: bool):
        try:
            with get_connection() as conn:
                conn.execute("UPDATE spy_sources SET enable_defense = ? WHERE id = ?", 
                            (1 if enable_defense else 0, source_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"更新防御状态失败: {e}")
            return False
