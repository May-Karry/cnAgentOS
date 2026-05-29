import json
from app.models.db import get_connection, init_db


def adjust_menu_hierarchy():
    """调整菜单层级关系"""
    init_db()
    
    with get_connection() as conn:
        print("正在查询菜单...")
        
        # 查询所有菜单
        cursor = conn.execute("SELECT id, name, url, parent_id FROM menus")
        all_menus = list(cursor.fetchall())
        
        print("\n当前菜单：")
        for menu in all_menus:
            print(f"  id={menu[0]}, name={menu[1]}, url={menu[2]}, parent_id={menu[3]}")
        
        # 找到需要调整的菜单
        watchtower_id = None
        data_warehouse_id = None
        forgery_id = None
        storage_id = None
        
        for menu in all_menus:
            if menu[2] == '/admin/watchtower':  # 瞭望管理
                watchtower_id = menu[0]
            if menu[2] == '/admin/data-warehouse':  # 数据仓库
                data_warehouse_id = menu[0]
            if menu[2] == '/admin/forgery-defense':  # 请求伪造防御
                forgery_id = menu[0]
            if menu[2] == '/admin/storage-manager':  # 存储配置管理
                storage_id = menu[0]
        
        print(f"\n找到的父菜单：")
        print(f"  瞭望管理: id={watchtower_id}")
        print(f"  数据仓库: id={data_warehouse_id}")
        print(f"  请求伪造防御: id={forgery_id}")
        print(f"  存储配置管理: id={storage_id}")
        
        # 更新层级关系
        print("\n正在调整...")
        
        if forgery_id and watchtower_id:
            conn.execute("UPDATE menus SET parent_id = ? WHERE id = ?", 
                        (watchtower_id, forgery_id))
            print(f"✓ 请求伪造防御 → 移动到 瞭望管理 内部")
        
        if storage_id and data_warehouse_id:
            conn.execute("UPDATE menus SET parent_id = ? WHERE id = ?", 
                        (data_warehouse_id, storage_id))
            print(f"✓ 存储配置管理 → 移动到 数据仓库 内部")
        
        conn.commit()
        
        print("\n菜单层级调整完成！")
        
        # 显示调整后的菜单
        cursor = conn.execute("SELECT id, name, url, parent_id FROM menus ORDER BY id")
        print("\n调整后的菜单：")
        for menu in cursor.fetchall():
            print(f"  id={menu[0]}, name={menu[1]}, url={menu[2]}, parent_id={menu[3]}")


if __name__ == "__main__":
    print("开始调整菜单层级...\n")
    adjust_menu_hierarchy()
    print("\n完成！请刷新页面查看效果！")