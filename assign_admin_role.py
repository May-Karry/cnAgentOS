from app.models.db import init_db, get_connection
from app.models.system import RoleRepository

def assign_admin_role():
    init_db()
    
    with get_connection() as conn:
        # 检查admin用户是否已有角色
        cursor = conn.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        if not admin_user:
            print("admin用户不存在")
            return
        
        admin_user_id = admin_user['id']
        
        # 获取超级管理员角色
        cursor = conn.execute("SELECT id FROM roles WHERE code = 'admin'")
        admin_role = cursor.fetchone()
        if not admin_role:
            print("超级管理员角色不存在")
            return
        
        admin_role_id = admin_role['id']
        
        # 检查是否已分配
        cursor = conn.execute("SELECT user_id FROM user_roles WHERE user_id = ?", (admin_user_id,))
        existing = cursor.fetchone()
        if existing:
            # 更新
            conn.execute("DELETE FROM user_roles WHERE user_id = ?", (admin_user_id,))
            conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (admin_user_id, admin_role_id))
            print("已更新admin用户角色为超级管理员")
        else:
            # 插入
            conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (admin_user_id, admin_role_id))
            print("已为admin用户分配超级管理员角色")
        
        conn.commit()

if __name__ == "__main__":
    assign_admin_role()
