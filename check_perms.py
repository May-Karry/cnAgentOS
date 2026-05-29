from app.models.db import init_db, get_connection

def check_permissions():
    init_db()
    
    with get_connection() as conn:
        print("=== 角色列表 ===")
        cursor = conn.execute("SELECT id, name, code, is_system FROM roles")
        for row in cursor.fetchall():
            print(f"ID: {row['id']}, 名称: {row['name']}, 代码: {row['code']}, 是否系统: {row['is_system']}")
        
        print("\n=== 菜单列表 ===")
        cursor = conn.execute("SELECT id, name, url FROM menus")
        for row in cursor.fetchall():
            print(f"ID: {row['id']}, 名称: {row['name']}, URL: {row['url']}")
        
        print("\n=== 角色菜单权限 ===")
        cursor = conn.execute("""
            SELECT r.name as role_name, m.name as menu_name, m.url 
            FROM role_menus rm
            JOIN roles r ON rm.role_id = r.id
            JOIN menus m ON rm.menu_id = m.id
            ORDER BY r.id, m.id
        """)
        for row in cursor.fetchall():
            print(f"角色: {row['role_name']}, 菜单: {row['menu_name']}, URL: {row['url']}")
        
        print("\n=== 用户角色关系 ===")
        cursor = conn.execute("""
            SELECT u.username, r.name as role_name
            FROM user_roles ur
            JOIN users u ON ur.user_id = u.id
            JOIN roles r ON ur.role_id = r.id
        """)
        for row in cursor.fetchall():
            print(f"用户: {row['username']}, 角色: {row['role_name']}")

if __name__ == "__main__":
    check_permissions()
