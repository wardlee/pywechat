"""
测试获取历史记录API
"""
import requests

BASE_URL = "http://localhost:5200"

def test_get_chat_history():
    """测试获取聊天历史记录"""
    
    # 测试1: 获取默认20条记录
    print("=" * 50)
    print("测试1: 获取默认20条历史记录")
    print("=" * 50)
    
    friend_name = "佳霖"  # 替换为实际的好友名称
    response = requests.get(f"{BASE_URL}/api/message/history", params={
        "friend_name": friend_name
    })
    
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    print(response.text)
    print()
    
    # 测试2: 获取指定条数（例如10条）
    print("=" * 50)
    print("测试2: 获取10条历史记录")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/message/history", params={
        "friend_name": friend_name,
        "limit": 10
    })
    
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    print(response.text)
    print()
    
    # 测试3: 查询不存在的好友（应该返回"没有记录"）
    print("=" * 50)
    print("测试3: 查询不存在的好友")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/message/history", params={
        "friend_name": "不存在的好友123"
    })
    
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    print(response.text)
    print()
    
    # 测试4: 缺少friend_name参数（应该返回400错误）
    print("=" * 50)
    print("测试4: 缺少friend_name参数（预期失败）")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/message/history")
    
    print(f"状态码: {response.status_code}")
    print("响应内容:")
    print(response.text)
    print()


if __name__ == "__main__":
    try:
        test_get_chat_history()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务已启动（运行 python app.py）")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
