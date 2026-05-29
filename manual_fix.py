import json
import re
from app.models.db import get_connection, init_db
from app.models.system import ForgeryTemplateRepository, StorageConfigRepository


def fix_app():
    """手动修复 app.py 中的 json 变量作用域问题"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 第一步：在 SpyCollectHandler 开头添加 re 和 json 导入
    old_header = '''    @tornado.web.authenticated
    def post(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            import traceback'''
    
    new_header = '''    @tornado.web.authenticated
    def post(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            import traceback
            import re
            import json'''
    
    # 第二步：删除内部的 import re 和 import json
    old_block = '''                                    # 如果还没找到，尝试从 data 中获取
                                    if not title or not item_url:
                                        # 尝试从 data 注释中提取
                                        data_comment = item.find(string=lambda s: s and 'title' in s and 'titleUrl' in s)
                                        if data_comment:
                                            try:
                                                import re
                                                # 查找 s-data: 后的 JSON
                                                match = re.search(r's-data:\\s*({.+})', data_comment)
                                                if match:
                                                    import json
                                                    s_data = json.loads(match.group(1))
                                                    if not title:
                                                        title = s_data.get("title", "")
                                                    if not item_url:
                                                        item_url = s_data.get("titleUrl", "")
                                                    if not summary:
                                                        summary = s_data.get("summary", "")
                                            except:
                                                pass'''
    
    new_block = '''                                    # 如果还没找到，尝试从 data 中获取
                                    if not title or not item_url:
                                        # 尝试从 data 注释中提取
                                        data_comment = item.find(string=lambda s: s and 'title' in s and 'titleUrl' in s)
                                        if data_comment:
                                            try:
                                                # 查找 s-data: 后的 JSON
                                                match = re.search(r's-data:\\s*({.+})', data_comment)
                                                if match:
                                                    s_data = json.loads(match.group(1))
                                                    if not title:
                                                        title = s_data.get("title", "")
                                                    if not item_url:
                                                        item_url = s_data.get("titleUrl", "")
                                                    if not summary:
                                                        summary = s_data.get("summary", "")
                                            except:
                                                pass'''
    
    # 应用修复
    if old_header in content:
        content = content.replace(old_header, new_header)
    
    if old_block in content:
        content = content.replace(old_block, new_block)
    
    # 保存
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 已修复 json/re 变量作用域问题")
    return True


def fix_menu_and_permissions():
    """修复菜单和权限问题"""
    init_db()
    
    with get_connection() as conn:
        # 1. 首先，确保菜单存在
        print("检查菜单...")
        
        # 查询数据仓库菜单
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/data-warehouse'")
        data_warehouse = cursor.fetchone()
        parent_id = data_warehouse[0] if data_warehouse else 0
        
        # 添加请求伪造防御菜单（如果不存在）
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/forgery-defense'")
        if not cursor.fetchone():
            conn.execute(
                "INSERT INTO menus (parent_id, name, url, icon, order_num) VALUES (?, ?, ?, ?, ?)",
                (parent_id, "请求伪造防御", "/admin/forgery-defense", "layui-icon-util", 6)
            )
            print("✓ 添加了请求伪造防御菜单")
        else:
            print("请求伪造防御菜单已存在")
        
        # 添加存储配置管理菜单（如果不存在）
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/storage-manager'")
        if not cursor.fetchone():
            conn.execute(
                "INSERT INTO menus (parent_id, name, url, icon, order_num) VALUES (?, ?, ?, ?, ?)",
                (parent_id, "存储配置管理", "/admin/storage-manager", "layui-icon-util", 7)
            )
            print("✓ 添加了存储配置管理菜单")
        else:
            print("存储配置管理菜单已存在")
        
        # 2. 给超级管理员角色分配新菜单的权限
        print("\n分配权限...")
        
        # 获取超级管理员角色
        cursor = conn.execute("SELECT id FROM roles WHERE code = 'admin'")
        admin_role = cursor.fetchone()
        
        if admin_role:
            role_id = admin_role[0]
            
            # 获取所有菜单
            cursor = conn.execute("SELECT id, url FROM menus")
            menus = list(cursor.fetchall())
            
            # 获取新添加的菜单的ID
            new_menus = []
            for menu_id, url in menus:
                if url in ['/admin/forgery-defense', '/admin/storage-manager']:
                    new_menus.append(menu_id)
            
            # 给超级管理员添加新菜单的权限
            for menu_id in new_menus:
                # 检查是否已有此权限
                cursor = conn.execute("SELECT * FROM role_menus WHERE role_id = ? AND menu_id = ?", 
                                      (role_id, menu_id))
                if not cursor.fetchone():
                    conn.execute("INSERT INTO role_menus (role_id, menu_id) VALUES (?, ?)",
                                (role_id, menu_id))
                    print(f"✓ 给超级管理员添加了菜单 {menu_id} 的权限")
        
        conn.commit()
        print("\n菜单和权限修复完成！")


if __name__ == "__main__":
    print("开始修复...\n")
    
    fix_app()
    fix_menu_and_permissions()
    
    print("\n所有修复完成！")
    print("\n接下来请重启服务：")
    print("1. 停止当前服务")
    print("2. 运行：python app.py")