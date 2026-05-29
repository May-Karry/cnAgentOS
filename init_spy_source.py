import json
from app.models.db import init_db, get_connection
from app.models.system import SpySourceRepository

def init_default_source():
    init_db()
    
    # 检查是否已有数据
    sources = SpySourceRepository.get_all_sources()
    if len(sources) > 0:
        print("数据源已存在，无需初始化")
        return
    
    # 百度新闻采集源配置
    entry_url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={keyword}"
    
    request_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    
    source_id = SpySourceRepository.create_source(
        name="百度新闻",
        entry_url=entry_url,
        request_headers=json.dumps(request_headers)
    )
    
    if source_id > 0:
        print("默认数据源已创建：百度新闻")
    else:
        print("创建失败")

if __name__ == "__main__":
    init_default_source()
