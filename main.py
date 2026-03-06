import requests
import os
import sys

# 1. 核心配置
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY")
MY_KEYWORD = "AI"  # 必须和钉钉机器人后台一致

def get_data():
    """获取 GitHub Trending"""
    try:
        r = requests.get("https://api.gitterapp.com/", timeout=15)
        return "\n".join([f"- {i['author']}/{i['name']}: {i['description']}" for i in r.json()[:5]])
    except:
        return "GitHub 热门项目获取暂时不可用"

def ask_ai(content):
    """阿里百炼专用调用逻辑"""
    # 阿里百炼兼容 OpenAI 的标准 Base URL
    api_url = "https://coding.dashscope.aliyuncs.com/v1" 
    
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    # 百炼模型名一定要写对，推荐使用以下两个之一：
    # "deepseek-v3" 或 "qwen-plus"
    data = {
        "model": "qwen3-coder-plus", 
        "messages": [
            {"role": "system", "content": f"你是一个技术专家。输出必须包含关键词：{MY_KEYWORD}"},
            {"role": "user", "content": f"请用中文精炼总结以下技术新闻：\n{content}"}
        ]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        # 增加状态码检查，防止解析非 JSON 内容
        if response.status_code != 200:
            return f"百炼服务器返回错误 (状态码 {response.status_code}): {response.text}"
            
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
        
    except Exception as e:
        return f"接口连接异常: {str(e)}"

def send_dingtalk(text):
    """发送到钉钉"""
    # 再次确保开头有关键词，防止被钉钉拦截
    safe_text = f"### {MY_KEYWORD} \n\n {text}"
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": "AI前沿简报", "text": safe_text}
    }
    r = requests.post(WEBHOOK, json=payload).json()
    if r.get("errcode") == 0:
        print("✅ 推送成功！")
    else:
        print(f"❌ 钉钉返回错误: {r}")

if __name__ == "__main__":
    raw_info = get_data()
    summary = ask_ai(raw_info)
    send_dingtalk(summary)
