import requests
import os
import sys

# 1. 变量获取 (从 GitHub Secrets)
WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
AI_KEY = os.getenv("LLM_API_KEY")
MY_KEYWORD = "AI" # 请确保钉钉机器人后台设置了此关键词

def diagnose_and_push():
    print("🔍 开始系统诊断...")
    
    # --- 诊断 A: 检查环境变量是否成功加载 ---
    if not AI_KEY or len(AI_KEY) < 10:
        msg = "❌ 诊断失败: LLM_API_KEY 为空或长度异常，请检查 GitHub Secrets 设置。"
        print(msg)
        return msg

    # --- 诊断 B: 阿里百炼 API 测试 ---
    # 使用阿里百炼标准兼容地址
    api_url = "https://coding.dashscope.aliyuncs.com/v1"
    
    headers = {
        "Authorization": f"Bearer {AI_KEY.strip()}", # strip() 防止前后空格干扰
        "Content-Type": "application/json"
    }
    
    # 使用最基础的模型 qwen-plus (通常默认开通)
    data = {
        "model": "qwen3-coder-plus", 
        "messages": [
            {"role": "user", "content": "你好，请回复'连接成功'"}
        ]
    }

    print(f"📡 正在请求百炼接口: {api_url}")
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=20)
        status_code = response.status_code
        
        if status_code == 200:
            ai_res = response.json()['choices'][0]['message']['content']
            diag_result = f"✅ AI 联通成功！回传内容: {ai_res}"
        elif status_code == 401:
            diag_result = f"❌ 鉴权失败 (401): 你的 API Key 依然无效。报错: {response.text}"
        elif status_code == 404:
            diag_result = f"❌ 地址错误 (404): 请检查 api_url 是否拼写正确。"
        else:
            diag_result = f"❌ 其他错误 ({status_code}): {response.text}"
            
    except Exception as e:
        diag_result = f"💥 网络请求崩溃: {str(e)}"

    print(diag_result)
    
    # --- 诊断 C: 推送至钉钉 ---
    print("📡 正在尝试推送到钉钉...")
    # 强制加上关键词
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "系统诊断报告",
            "text": f"### {MY_KEYWORD} 系统诊断\n\n**结果**: {diag_result}"
        }
    }
    
    try:
        r = requests.post(WEBHOOK, json=payload).json()
        if r.get("errcode") == 0:
            print("🚀 钉钉推送成功，请查看手机！")
        else:
            print(f"❌ 钉钉拒绝推送: {r.get('errmsg')}")
    except Exception as e:
        print(f"❌ 钉钉连接失败: {e}")

if __name__ == "__main__":
    diagnose_and_push()
