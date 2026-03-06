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


