from app.models.db import init_db, get_connection

def init_default_data():
    init_db()
    
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, code FROM roles")
        existing_roles = {row['code']: row['id'] for row in cursor.fetchall()}
        
        if 'admin' not in existing_roles:
            conn.execute("INSERT INTO roles (name, code, is_system) VALUES ('超级管理员', 'admin', 1)")
            print("已创建超级管理员角色")
        
        if 'user' not in existing_roles:
            conn.execute("INSERT INTO roles (name, code, is_system) VALUES ('普通用户', 'user', 0)")
            print("已创建普通用户角色")
        
        if 'user_admin' not in existing_roles:
            conn.execute("INSERT INTO roles (name, code, is_system) VALUES ('用户管理员', 'user_admin', 0)")
            print("已创建用户管理员角色")
        
        cursor = conn.execute("SELECT id, code FROM roles")
        existing_roles = {row['code']: row['id'] for row in cursor.fetchall()}
        
        cursor = conn.execute("SELECT COUNT(*) FROM menus")
        count = cursor.fetchone()[0]
        
        if count == 0:
            menus = [
                (1, 0, '用户管理', '/admin/users', 'layui-icon-user', 1),
                (2, 0, '功能管理', '/admin/functions', 'layui-icon-set', 2),
                (3, 0, '权限管理', '/admin/permissions', 'layui-icon-password', 3),
                (4, 0, '数字员工', '/admin/digital-staff', 'layui-icon-dialogue', 4),
                (5, 0, '模型引擎', '/admin/model-engine', 'layui-icon-release', 5),
                (6, 0, '瞭望管理', '/admin/watchtower', 'layui-icon-search', 6),
                (7, 0, '数据仓库', '/admin/data-warehouse', 'layui-icon-survey', 7),
                (8, 0, '深度采集', '/admin/deep-collection', 'layui-icon-upload', 8),
                (9, 0, '接口管理', '/admin/api-management', 'layui-icon-link', 9),
                (10, 0, '数智大屏', '/admin/dashboard', 'layui-icon-chart-screen', 10),
                (11, 0, '系统设置', '/admin/system-settings', 'layui-icon-set-fill', 11),
                (12, 0, '系统统计', '/admin/system-stats', 'layui-icon-chart', 12),
            ]
            
            for menu in menus:
                conn.execute("INSERT INTO menus (id, parent_id, name, url, icon, order_num) VALUES (?, ?, ?, ?, ?, ?)", menu)
            
            print("已创建12个默认功能模块")
            
            cursor = conn.execute("SELECT id FROM roles WHERE code = 'admin'")
            admin_role = cursor.fetchone()
            if admin_role:
                admin_role_id = admin_role[0]
                cursor = conn.execute("SELECT id FROM menus")
                menu_ids = [row[0] for row in cursor.fetchall()]
                for menu_id in menu_ids:
                    conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", (admin_role_id, menu_id))
                print("已为超级管理员分配所有功能权限")
            
            cursor = conn.execute("SELECT id FROM roles WHERE code = 'user'")
            user_role = cursor.fetchone()
            if user_role:
                user_role_id = user_role[0]
                cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/users'")
                user_menu = cursor.fetchone()
                if user_menu:
                    conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", (user_role_id, user_menu[0]))
                print("已为普通用户分配基本功能权限")
            
            cursor = conn.execute("SELECT id FROM roles WHERE code = 'user_admin'")
            user_admin_role = cursor.fetchone()
            if user_admin_role:
                user_admin_role_id = user_admin_role[0]
                cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/users'")
                user_menu = cursor.fetchone()
                if user_menu:
                    conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", (user_admin_role_id, user_menu[0]))
                print("已为用户管理员分配用户管理权限")
            
            conn.commit()
        else:
            print("功能模块已存在，跳过初始化")

if __name__ == "__main__":
    init_default_data()