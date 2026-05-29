import requests
from bs4 import BeautifulSoup
import urllib.parse
import traceback

def test_crawl():
    url = "https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word=" + urllib.parse.quote("人工智能")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    
    print(f"请求: {url}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # 保存页面用于分析
            with open("test_page.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("页面已保存到 test_page.html")
            
            # 尝试多种选择器
            selectors = [
                "div.result",
                "div.c-container", 
                "article",
                ".news-list-item",
                ".result-item"
            ]
            
            for sel in selectors:
                items = soup.select(sel)
                if items:
                    print(f"\n选择器 {sel} 找到 {len(items)} 条")
                    for i, item in enumerate(items[:3]):
                        print(f"  第{i+1}条:")
                        print(f"    内容: {str(item)[:150]}")
            
            # 查找所有链接
            links = soup.find_all("a")
            print(f"\n找到 {len(links)} 个链接")
            
            # 查找所有包含文字的 div
            all_divs = soup.find_all("div")
            print(f"找到 {len(all_divs)} 个 div")
            
            return True
    except Exception as e:
        print(f"出错: {e}")
        print(traceback.format_exc())
    
    return False

if __name__ == "__main__":
    test_crawl()
