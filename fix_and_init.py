import json
import re
from app.models.db import get_connection, init_db
from app.models.system import ForgeryTemplateRepository, StorageConfigRepository


def fix_json_scope_issue():
    """修复采集代码中 json 变量作用域问题"""
    init_db()
    
    # 读取 app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否需要修复
    if "import json" not in content[content.find("data_comment = item.find"):content.find("data_comment = item.find") + 500]:
        print("json 作用域问题可能已修复或不需要修复")
        return False
    
    # 替换问题代码
    old_code = '''                                    # 如果还没找到，尝试从 data 中获取
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
    
    new_code = '''                                    # 如果还没找到，尝试从 data 中获取
                                    if not title or not item_url:
                                        # 尝试从 data 注释中提取
                                        import re
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
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 已修复 json 变量作用域问题")
        return True
    else:
        print("未找到需要修复的代码，可能已经修复")
        return False


def init_forgery_templates():
    init_db()
    
    # 检查是否已有模板
    templates = ForgeryTemplateRepository.get_all_templates()
    if len(templates) > 0:
        print("伪造模板已存在，跳过初始化")
        return
    
    # 创建默认模板
    ForgeryTemplateRepository.create_template(
        name="CSRF 基础测试",
        attack_type="CSRF",
        description="模拟跨站请求伪造攻击",
        headers=json.dumps({
            "Referer": "http://legitimate-site.com",
            "Origin": "http://legitimate-site.com",
            "X-Requested-With": "XMLHttpRequest"
        }),
        payloads=json.dumps({
            "action": "transfer",
            "amount": 1000
        })
    )
    
    ForgeryTemplateRepository.create_template(
        name="SSRF 本地探测",
        attack_type="SSRF",
        description="探测本地服务",
        headers=json.dumps({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }),
        payloads=json.dumps({})
    )
    
    print("默认伪造模板已创建")


def init_storage_configs():
    init_db()
    
    configs = StorageConfigRepository.get_all_configs()
    if len(configs) > 0:
        print("存储配置已存在，跳过初始化")
        return
    
    # 创建示例配置
    StorageConfigRepository.create_config(
        name="本地 SQLite",
        storage_type="sqlite",
        connection_string="app.db",
        config=json.dumps({})
    )
    
    StorageConfigRepository.create_config(
        name="示例 MongoDB",
        storage_type="mongodb",
        connection_string="mongodb://localhost:27017",
        config=json.dumps({"db": "mydb"})
    )
    
    StorageConfigRepository.create_config(
        name="示例 Redis",
        storage_type="redis",
        connection_string="redis://localhost:6379",
        config=json.dumps({"db": 0})
    )
    
    print("示例存储配置已创建")


def init_menus():
    """初始化新页面的菜单"""
    init_db()
    
    with get_connection() as conn:
        # 检查是否已有请求伪造防御菜单
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/forgery-defense'")
        if not cursor.fetchone():
            # 获取数据仓库菜单位置
            cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/data-warehouse'")
            row = cursor.fetchone()
            parent_id = row[0] if row else 0
            
            # 添加请求伪造防御菜单
            conn.execute(
                "INSERT INTO menus (parent_id, name, url, icon, order_num) VALUES (?, ?, ?, ?, ?)",
                (parent_id, "请求伪造防御", "/admin/forgery-defense", "layui-icon-util", 6)
            )
            print("请求伪造防御菜单已添加")
        
        # 检查是否已有存储配置管理菜单
        cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/storage-manager'")
        if not cursor.fetchone():
            # 获取数据仓库菜单位置
            cursor = conn.execute("SELECT id FROM menus WHERE url = '/admin/data-warehouse'")
            row = cursor.fetchone()
            parent_id = row[0] if row else 0
            
            # 添加存储配置管理菜单
            conn.execute(
                "INSERT INTO menus (parent_id, name, url, icon, order_num) VALUES (?, ?, ?, ?, ?)",
                (parent_id, "存储配置管理", "/admin/storage-manager", "layui-icon-util", 7)
            )
            print("存储配置管理菜单已添加")
        
        conn.commit()


if __name__ == "__main__":
    print("开始修复...")
    
    # 1. 修复 json 作用域问题
    fix_json_scope_issue()
    
    # 2. 初始化数据
    init_forgery_templates()
    init_storage_configs()
    
    # 3. 初始化菜单
    init_menus()
    
    print("\n修复完成！")
    print("\n接下来请：")
    print("1. 重启服务：python app.py")
    print("2. 访问：http://localhost:10086/admin/index")
    print("3. 使用超级管理员账号登录")
    print("4. 就可以在侧边栏看到新菜单项了")