import requests
import os
import sys

# 1. 核心变量 (已验证)
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY").strip()
MY_KEYWORD = "AI" 

def get_github_trending():
    """获取 GitHub 今日最火的 5 个项目"""
    url = "https://api.gitterapp.com/"
    try:
        repos = requests.get(url, timeout=15).json()[:5]
        return "\n".join([f"- **{r['author']}/{r['name']}**: {r['description']}" for r in repos])
    except:
        return "GitHub 数据抓取暂时失效，请检查网络。"

def ask_ai_final(content):
    """阿里百炼正式总结逻辑"""
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    # 既然已经验证成功，这里我们放心使用 deepseek-v3 或 qwen-plus
    data = {
        "model": "qwen3.5-plus", 
        "messages": [
            {"role": "system", "content": f"你是一个科技博主。你的输出开头必须包含关键词：{MY_KEYWORD}"},
            {"role": "user", "content": f"请用中文简洁总结这些 GitHub 项目，并点评其价值：\n{content}"}
        ]
    }
    
    try:
        res = requests.post(api_url, headers=headers, json=data, timeout=30).json()
        return res['choices'][0]['message']['content']
    except:
        return f"AI 总结环节出错。原始内容如下：\n{content}"

def send_final(text):
    """最终推送到钉钉"""
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "今日 AI 简报",
            "text": text # 关键词已经在 AI 生成的内容里了
        }
    }
    requests.post(WEBHOOK, json=payload)

if __name__ == "__main__":
    print("🚀 启动最终任务...")
    raw_data = get_github_trending()
    final_content = ask_ai_final(raw_data)
    send_final(final_content)
    print("✅ 全部完成！去钉钉看看你的正式简报吧。")
