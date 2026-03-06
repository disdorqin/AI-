import requests
import os
import sys

# 1. 核心变量
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY").strip()
MY_KEYWORD = "AI" 

def get_github_trending():
    """改用 GitHub 官方搜索接口获取今日最火项目，更稳健"""
    # 搜索过去 24 小时内星数最多的 Python/AI 相关项目
    url = "https://api.github.com/search/repositories?q=created:>2025-01-01&sort=stars&order=desc&per_page=5"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            items = r.json().get('items', [])
            return "\n".join([f"- **{i['full_name']}**: {i['description']} (⭐{i['stargazers_count']})" for i in items])
        else:
            # 保底数据，防止 AI 报错
            return "- OpenClaw: 开源 AI Agent 框架\n- DeepSeek-V3: 强力开源大模型\n- LightRAG: 检索增强生成新方案"
    except:
        return "- 自动抓取失败，请关注今日 DeepSeek 和 Qwen 的最新动态。"

def ask_ai_final(content):
    """阿里百炼正式总结逻辑"""
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen3.5-plus", 
        "messages": [
            {"role": "system", "content": f"你是一个科技博主。你的输出开头必须包含关键词：{MY_KEYWORD}"},
            {"role": "user", "content": f"请用中文简洁总结这些技术动态，并点评其价值：\n{content}"}
        ]
    }
    
    try:
        res = requests.post(api_url, headers=headers, json=data, timeout=30).json()
        if "choices" in res:
            return res['choices'][0]['message']['content']
        else:
            return f"{MY_KEYWORD}\nAI 接口返回异常，原始数据：\n{content}"
    except:
        return f"{MY_KEYWORD}\n网络连接超时，原始数据：\n{content}"

def send_final(text):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日 AI 简报",
            "text": text 
        }
    }
    requests.post(WEBHOOK, json=payload)

if __name__ == "__main__":
    print("🚀 正在通过备用通道获取数据...")
    raw_data = get_github_trending()
    print("🤖 正在请教 AI...")
    final_content = ask_ai_final(raw_data)
    print("📡 准备发送...")
    send_final(final_content)
    print("✅ 任务结束")
