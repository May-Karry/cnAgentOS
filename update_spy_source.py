import json
from app.models.db import get_connection
from app.models.system import SpySourceRepository

def update_source():
    sources = SpySourceRepository.get_all_sources()
    if len(sources) == 0:
        print("无数据源")
        return
    
    for source in sources:
        if source['name'] == '百度新闻':
            new_url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={keyword}"
            new_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
            }
            
            SpySourceRepository.update_source(
                source_id=source['id'],
                name='百度新闻',
                entry_url=new_url,
                request_headers=json.dumps(new_headers)
            )
            print("数据源已更新")

if __name__ == "__main__":
    update_source()
