import requests
import os
import time

# 核心变量
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY").strip()
MY_KEYWORD = "AI" 

def get_ai_news():
    """尝试抓取 AI 相关的最新动态/优惠信息"""
    # 这里我们换一个更泛 AI 资讯的接口（演示用，可以根据需要换成具体的优惠 RSS）
    url = "https://api.github.com/search/repositories?q=AI+deals+OR+awesome-ai&sort=updated"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            items = r.json().get('items', [])[:5]
            return "\n".join([f"- {i['name']}: {i['description']} (更新于:{i['updated_at']})" for i in items])
        return "无法获取实时优惠，请手动关注 DeepSeek/OpenAI 官网。"
    except:
        return "数据源访问受限。"

def ask_ai_with_retry(content, retries=3):
    """带重试机制的 AI 总结，解决超时问题"""
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
    
    data = {
        "model": "qwen3.5-plus", 
        "messages": [
            {"role": "system", "content": f"你是一个AI猎手，专门搜集AI白嫖、降价、优惠和重大更新。开头必须带关键词：{MY_KEYWORD}"},
            {"role": "user", "content": f"请把以下信息整理成『省钱/前沿』快报，重点突出优惠和白嫖价值：\n{content}"}
        ]
    }
    
    for i in range(retries):
        try:
            # 增加超时时间到 60s
            res = requests.post(api_url, headers=headers, json=data, timeout=60)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"尝试第 {i+1} 次失败: {e}")
            time.sleep(2) # 歇 2 秒再试
    return f"{MY_KEYWORD}\n AI 接口连续 {retries} 次超时，今日原始情报如下：\n{content}"

def send_final(text):
    payload = {"msgtype": "markdown", "markdown": {"title": "AI 优惠早报", "text": text}}
    requests.post(WEBHOOK, json=payload)

if __name__ == "__main__":
    news = get_ai_news()
    report = ask_ai_with_retry(news)
    send_final(report)
