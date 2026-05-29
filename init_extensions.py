import json
from app.models.db import get_connection, init_db
from app.models.system import ForgeryTemplateRepository, StorageConfigRepository


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


if __name__ == "__main__":
    init_forgery_templates()
    init_storage_configs()
    print("\n初始化完成！")