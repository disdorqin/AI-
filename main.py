import requests
import os

# 获取秘钥
webhook = os.getenv("DINGTALK_WEBHOOK")

def test_push():
    # 注意：这里的 text 必须包含你在钉钉后台设置的“关键词”！
    # 假设你的关键词是“AI简报”
    data = {
        "msgtype": "text",
        "text": {"content": "测试推送：这是一条来自 GitHub 的 AI简报 测试消息"}
    }
    res = requests.post(webhook, json=data)
    print(f"状态码: {res.status_code}")
    print(f"返回结果: {res.text}")

if __name__ == "__main__":
    test_push()

"""
import requests
import os
import json

# 从 GitHub Secrets 中读取你配置好的秘钥
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def get_data():
    """抓取 GitHub 今日最火的 5 个项目"""
    url = "https://api.gitterapp.com/"  # 这是一个好用的镜像接口
    try:
        repos = requests.get(url, timeout=10).json()[:5]
        content = "\n".join([f"- **{r['author']}/{r['name']}**: {r['description']} (⭐{r['stars']})" for r in repos])
        return content
    except Exception as e:
        return f"数据抓取失败: {e}"

def ask_ai(raw_content):
    """调用 AI 总结内容 (包含钉钉关键词：AI简报)"""
    # 这里建议使用 DeepSeek 或 Gemini 的 API 地址
    # 如果你用的是 One API，请换成你的中转地址
    api_url = "https://api.deepseek.com/v1/chat/completions" 
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 注意：prompt 里必须带上你在钉钉设置的“自定义关键词”
    prompt = f"你是一个技术专家。请将以下 GitHub 热门项目总结成一份精简的微信风格『AI简报』，要求逻辑清晰，使用 Markdown 格式，包含加粗列表，必须包含关键词『AI简报』：\n{raw_content}"
    
    data = {
        "model": "deepseek-chat", # 或者你有的其他模型
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI 总结失败，原始数据如下：\n{raw_content}"

def send_dingtalk(text):
    """发送到钉钉"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日 AI 前沿简报",
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, json=payload)

if __name__ == "__main__":
    # 逻辑：抓取 -> 总结 -> 推送
    raw_data = get_data()
    final_report = ask_ai(raw_data)
    send_dingtalk(final_report)

