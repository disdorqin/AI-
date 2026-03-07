import requests
import os
import time

# 核心变量
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY", "").strip()
MY_KEYWORD = "AI" 

def get_github_repos():
    """抓取最新、最热的 AI 开源项目"""
    # 搜索包含 AI/LLM 标签，且最近有更新的顶级项目
    url = "https://api.github.com/search/repositories?q=topic:ai+OR+topic:llm&sort=updated&order=desc&per_page=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            items = r.json().get('items', [])
            return "\n".join([f"- **{i['name']}** (⭐{i['stargazers_count']}): {i['description']}" for i in items])
        return "GitHub 热门获取受限。"
    except Exception as e:
        return f"GitHub 请求异常: {e}"

def get_hacker_news():
    """抓取 Hacker News 上最新的 AI 科技头条（极客最前沿）"""
    # Algolia 提供的 HN 实时搜索 API，搜索 AI 或大模型相关新闻
    url = "https://hn.algolia.com/api/v1/search_by_date?query=AI+OR+LLM+OR+DeepSeek&tags=story&hitsPerPage=6"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            hits = r.json().get('hits', [])
            return "\n".join([f"- {h.get('title', '无标题')} (作者: {h.get('author', '佚名')})" for h in hits])
        return "新闻源获取受限。"
    except Exception as e:
        return f"新闻请求异常: {e}"

def ask_ai_with_retry(github_content, news_content, retries=3):
    """带重试机制的 AI 总结引擎"""
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
    
    # 精心设计的 Prompt，让 AI 扮演情报分析师
    prompt = f"""
    你是一个极其专业的 AI 科技情报官。请根据以下两部分原始数据，为我生成一份高质量的微信排版风格简报。
    
    要求：
    1. 【核心强制】第一行必须包含关键词：{MY_KEYWORD}
    2. 分为两个模块：「🔥 GitHub 潜力开源库」和「📰 硅谷 AI 前沿快讯」。
    3. 用中文简明扼要地解释每个项目/新闻的价值，如果发现有可能是免费工具或优惠信息，请用 💰 表情重点标出！
    4. 语气要Geek、专业且有感染力。
    
    [GitHub 数据]
    {github_content}
    
    [Hacker News 数据]
    {news_content}
    """

    data = {
        "model": "qwen3.5-plus", 
        "messages": [
            {"role": "system", "content": "你是一个精准、高效的科技情报助手。"},
            {"role": "user", "content": prompt}
        ]
    }
    
    for i in range(retries):
        try:
            res = requests.post(api_url, headers=headers, json=data, timeout=60)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            else:
                print(f"API 报错 (状态码 {res.status_code}): {res.text}")
        except Exception as e:
            print(f"尝试第 {i+1} 次网络请求失败: {e}")
            time.sleep(3) 
            
    return f"### {MY_KEYWORD}\n\n⚠️ AI 总结服务暂时离线，为您播报今日原始数据：\n\n**GitHub:**\n{github_content}\n\n**News:**\n{news_content}"

def send_final(text):
    """推送 Markdown 到钉钉"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日 AI 极客情报",
            "text": text 
        }
    }
    r = requests.post(WEBHOOK, json=payload)
    if r.json().get("errcode") == 0:
        print("✅ 钉钉推送成功！")
    else:
        print(f"❌ 钉钉推送失败: {r.text}")

if __name__ == "__main__":
    print("🚀 正在探测 GitHub 实时开源库...")
    github_data = get_github_repos()
    
    print("📡 正在截获 Hacker News 前沿科技电报...")
    news_data = get_hacker_news()
    
    print("🤖 正在唤醒大模型进行情报分析...")
    final_report = ask_ai_with_retry(github_data, news_data)
    
    print("📤 正在下发至钉钉终端...")
    send_final(final_report)
    print("🎉 今日情报任务圆满结束！")
