from app.models.db import init_db, get_connection

def assign_user_admin_perms():
    init_db()
    
    with get_connection() as conn:
        # 获取用户管理员角色
        cursor = conn.execute("SELECT id FROM roles WHERE code = 'user_admin'")
        user_admin_role = cursor.fetchone()
        if not user_admin_role:
            print("用户管理员角色不存在")
            return
        
        user_admin_role_id = user_admin_role['id']
        
        # 获取用户管理菜单
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/users'")
        user_menu = cursor.fetchone()
        if not user_menu:
            print("用户管理菜单不存在")
            return
        
        user_menu_id = user_menu['id']
        
        # 检查是否已分配
        cursor = conn.execute("SELECT role_id FROM role_menus WHERE role_id = ? AND menu_id = ?", 
                            (user_admin_role_id, user_menu_id))
        existing = cursor.fetchone()
        
        if existing:
            print("用户管理员已有用户管理权限")
        else:
            conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", 
                        (user_admin_role_id, user_menu_id))
            conn.commit()
            print("已为用户管理员分配用户管理权限")
        
        # 同样为普通用户分配权限
        cursor = conn.execute("SELECT id FROM roles WHERE code = 'user'")
        user_role = cursor.fetchone()
        if user_role:
            user_role_id = user_role['id']
            cursor = conn.execute("SELECT role_id FROM role_menus WHERE role_id = ? AND menu_id = ?", 
                                (user_role_id, user_menu_id))
            existing = cursor.fetchone()
            
            if existing:
                print("普通用户已有用户管理权限")
            else:
                conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)", 
                            (user_role_id, user_menu_id))
                conn.commit()
                print("已为普通用户分配用户管理权限")

if __name__ == "__main__":
    assign_user_admin_perms()
