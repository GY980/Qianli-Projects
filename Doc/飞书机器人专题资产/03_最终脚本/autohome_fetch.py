# -*- coding: utf-8 -*-
"""
汽车之家资讯 · 抓取存档脚本(autohome_fetch.py)
用途:每晚 23:59 由 Windows 定时任务自动运行,抓取当天最新资讯并存档。
产出:①带日期的 md 存档(给人看);②latest_news.json(给发送脚本读)。
配套:autohome_send.py(次日早上读 json 发飞书)。
运行环境:Python 3 + requests + beautifulsoup4
"""
import re, os, json, requests
from datetime import datetime
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.autohome.com.cn/all/"   # 全部资讯列表页(严格倒序,排除首页置顶旧文)
MAX_ARTICLES = 12
ARTICLE_RE = re.compile(r"/(news|drive|tech|advice)/\d{4,6}/\d+\.html")

def fetch():
    headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")}
    resp = requests.get(SOURCE_URL, headers=headers, timeout=10)
    resp.encoding = resp.apparent_encoding
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    seen, out = set(), []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if not ARTICLE_RE.search(href):
            continue
        h = a.find(["h3", "h2"])          # 只取有 h3/h2 标题的,自动排除置顶推荐位、标题也干净
        if not h:
            continue
        title = h.get_text(strip=True)
        if len(title) < 6:
            continue
        full = href
        if full.startswith("//"): full = "https:" + full
        elif full.startswith("/"): full = "https://www.autohome.com.cn" + full
        if full in seen: continue
        seen.add(full)
        out.append({"title": title, "url": full})
        if len(out) >= MAX_ARTICLES: break
    return out

def main():
    day = datetime.now().strftime("%Y-%m-%d")
    articles = fetch()
    folder = os.path.dirname(os.path.abspath(__file__))
    md = [f"# 汽车之家资讯 · {day}", "", f"共 {len(articles)} 条", ""]
    for i, a in enumerate(articles, 1):
        md.append(f"{i}. [{a['title']}]({a['url']})")
    with open(os.path.join(folder, f"汽车之家资讯_{day}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(folder, "latest_news.json"), "w", encoding="utf-8") as f:
        json.dump({"day": day, "articles": articles}, f, ensure_ascii=False, indent=2)
    print(f"已抓取 {len(articles)} 条,存档完成:{day}")

if __name__ == "__main__":
    main()
