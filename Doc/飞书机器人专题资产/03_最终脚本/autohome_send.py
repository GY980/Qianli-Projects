# -*- coding: utf-8 -*-
"""
汽车之家资讯 · 读存档发飞书脚本(autohome_send.py)
用途:每天早上 9:00 由 Windows 定时任务自动运行,读取前一晚的存档,推送到飞书群。
配套:autohome_fetch.py(前一晚 23:59 抓取并生成 latest_news.json)。
运行环境:Python 3 + requests

⚠️ 使用前:把下面 FEISHU_WEBHOOK_URL 换成你自己的群机器人 webhook 地址。
   (归档版已抹去真实地址,防止密钥泄露)
"""
import os, json, requests

# 换成你自己的群机器人 webhook 地址
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/你的机器人key"

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, "latest_news.json")
    if not os.path.exists(path):
        print("没找到 latest_news.json,先运行 autohome_fetch.py 抓取。")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    day, articles = data["day"], data["articles"]
    if not articles:
        print("存档里没有文章。")
        return

    elements = []
    for i, a in enumerate(articles, 1):
        elements.append({"tag": "div", "text": {"tag": "lark_md",
                        "content": f"**{i}.** [{a['title']}]({a['url']})"}})
        if i < len(articles):
            elements.append({"tag": "hr"})
    card = {"msg_type": "interactive", "card": {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue",
                   "title": {"tag": "plain_text", "content": f"汽车之家 · {day} 资讯速递"}},
        "elements": elements + [
            {"tag": "hr"},
            {"tag": "note", "elements": [
                {"tag": "plain_text", "content": f"{day} 资讯汇总 · 次日推送"}]}
        ]}}

    r = requests.post(FEISHU_WEBHOOK_URL, headers={"Content-Type": "application/json"},
                      data=json.dumps(card), timeout=10).json()
    if r.get("code", 0) == 0 or r.get("StatusCode", 0) == 0:
        print("推送成功")
    else:
        print("推送失败:", r)

if __name__ == "__main__":
    main()
