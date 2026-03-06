import requests
import os
import sys

# 1. 核心配置
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY")
MY_KEYWORD = "AI"  # 确保这四个字在你的钉钉机器人设置里

def get_data():
    """抓取 GitHub 今日最火的 5 个项目"""
    url = "https://api.gitterapp.com/"
    try:
        repos = requests.get(url, timeout=15).json()[:5]
        return "\n".join([f"- **{r['author']}/{r['name']}**: {r['description']}" for r in repos])
    except Exception as e:
        return f"数据抓取异常: {e}"

def ask_ai(content):
    """调用 AI 总结内容"""
    # 如果你是用 One API 或中转，请修改下面这个 URL
    api_url = "https://api.deepseek.com/v1/chat/completions" 
    
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat", # 请确认你的 API 支持这个模型名
        "messages": [{"role": "user", "content": f"请简要总结以下技术新闻：\n{content}"}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        # 调试：如果在 Actions 日志里看到这行，能帮你定位 API 报错
        if "choices" not in res_json:
            return f"AI 接口报错了！返回内容是: {res_json}"
            
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 请求彻底失败: {e}"

def send_dingtalk(text):
    """发送到钉钉 (带上关键词强制通行)"""
    safe_text = f"### {MY_KEYWORD} \n\n {text}"
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": "今日资讯", "text": safe_text}
    }
    r = requests.post(WEBHOOK, json=payload).json()
    if r.get("errcode") == 0:
        print("✅ 推送成功")
    else:
        print(f"❌ 钉钉拒绝: {r.get('errmsg')}")

if __name__ == "__main__":
    print("🚀 开始收集...")
    raw = get_data()
    print("🤖 正在请教 AI...")
    summary = ask_ai(raw)
    print("📡 准备发送...")
    send_dingtalk(summary)
