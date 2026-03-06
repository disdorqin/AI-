import requests
import os
import sys

# 1. 读取环境变量
URL = os.getenv("DINGTALK_WEBHOOK")
KEY = os.getenv("LLM_API_KEY")

def send_ding(text):
    # 【注意】请把下方的 'AI简报' 换成你钉钉机器人后台设置的实际关键词！
    keyword = "AI简报" 
    final_text = f"{keyword}\n\n{text}"
    
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": "Daily News", "text": final_text}
    }
    
    # 发送请求并获取结果
    response = requests.post(URL, json=payload)
    result = response.json()
    
    print(f"DingTalk Response: {result}")
    
    # 如果钉钉返回错误，直接让脚本报错退出，这样 Actions 就会变红提醒你
    if result.get("errcode") != 0:
        print(f"Error: DingTalk push failed! Message: {result.get('errmsg')}")
        sys.exit(1)

def get_simple_data():
    return "- 项目: OpenClaw, 描述: 强大的本地智能体框架\n- 项目: DeepSeek-V3, 描述: 最强开源模型"

if __name__ == "__main__":
    # 为了测试，我们先发一段简单的内容，排除 AI 干扰
    test_content = get_simple_data()
    send_ding(test_content)
