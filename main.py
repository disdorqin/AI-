import requests
import os
import sys

# 1. 核心配置：从 GitHub Secrets 获取
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY")

# 钉钉关键词：必须和你机器人设置里的一模一样！
KEYWORD = "AI"

def get_github_trending():
    """抓取 GitHub Trending Top 5"""
    url = "https://api.gitterapp.com/"
    try:
        r = requests.get(url, timeout=10)
        repos = r.json()[:5]
        return "\n".join([f"- **{i['author']}/{i['name']}**: {i['description']} (⭐{i['stars']})" for i in repos])
    except:
        return "GitHub 抓取失败"

def get_hf_papers():
    """抓取 Hugging Face Daily Papers Top 5"""
    url = "https://huggingface.co/api/daily_papers"
    try:
        r = requests.get(url, timeout=10)
        papers = r.json()[:5]
        return "\n".join([f"- **{p['paper']['title']}**: {p['paper']['summary'][:100]}..." for p in papers])
    except:
        return "HF 论文抓取失败"

def ask_ai(content):
    """调用 AI 总结内容"""
    # 这里默认使用 DeepSeek API 地址，如果你用的是 One API 请更换为你的中转地址
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    你是一个资深科技博主。请根据以下原始信息，整理出一份极其精炼的微信风格技术简报。
    要求：
    1. 必须在开头第一行包含关键词：{KEYWORD}
    2. 使用 Markdown 格式，多用加粗和列表，让手机端易读。
    3. 将 GitHub 项目和 HF 论文分开展示，并对每个点进行一句话中文核心点点评。
    4. 结尾加一句幽默的『极客金句』。
    
    以下是原始信息：
    {content}
    """
    
    data = {
        "model": "deepseek-chat", # 这里可以根据你的 API 支持的模型来换，如 gpt-4o, gemini-pro
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        res = requests.post(api_url, headers=headers, json=data, timeout=30).json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 总结出现异常: {e}"

def send_dingtalk(text):
    """推送至钉钉"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日前沿 AI 简报",
            "text": text
        }
    }
    
    response = requests.post(WEBHOOK, json=payload)
    result = response.json()
    
    if result.get("errcode") == 0:
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result.get('errmsg')}")
        sys.exit(1)

if __name__ == "__main__":
    # 步骤：组合数据 -> 问 AI -> 发现场
    print("🚀 正在收集数据...")
    gh_data = get_github_trending()
    hf_data = get_hf_papers()
    
    combined_content = f"--- GitHub Trending ---\n{gh_data}\n\n--- HF Daily Papers ---\n{hf_data}"
    
    print("🤖 正在请求 AI 总结...")
    final_report = ask_ai(combined_content)
    
    print("📡 正在推送到钉钉...")
    send_dingtalk(final_report)
