"""
API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5200"

def test_send_message():
    """测试发送消息"""
    print("\n=== 测试发送消息 ===")
    
    # 单条消息
    response = requests.post(
        f"{BASE_URL}/api/message/send",
        json={
            "friend_name": "佳霖",
            "messages": "你好"
        }
    )
    print(f"单条消息: {response.json()}")
    
    # 多条消息
    response = requests.post(
        f"{BASE_URL}/api/message/send",
        json={
            "friend_name": "佳霖",
            "messages": ["我没事", "我能有啥事啊", "就问下"]
        }
    )
    print(f"多条消息: {response.json()}")


def test_get_latest():
    """测试获取最新消息"""
    print("\n=== 测试获取最新消息 ===")
    
    # 获取所有未读消息
    response = requests.get(f"{BASE_URL}/api/message/latest")
    print(f"所有未读: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 获取指定好友的未读消息
    response = requests.get(f"{BASE_URL}/api/message/latest?friend_name=佳霖")
    print(f"佳霖的未读: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_monitor_list():
    """测试监听列表"""
    print("\n=== 测试监听列表 ===")
    
    # 设置监听列表
    response = requests.post(
        f"{BASE_URL}/api/monitor/set",
        json={
            "friends": ["佳霖","晓D"]
        }
    )
    print(f"设置监听列表: {response.json()}")
    
def get_monitor_list():    
    # 获取监听列表
    response = requests.get(f"{BASE_URL}/api/monitor/list")
    print(f"当前监听列表: {response.json()}")


if __name__ == "__main__":
    try:
        # 测试根路径
        response = requests.get(BASE_URL)
        print(f"\n服务状态: {response.json()}")
        
        # 设置监听列表
        # test_monitor_list()
        # 获取监听列表
        # get_monitor_list()
        # test_send_message()
        # test_get_latest()
        
        print("✓ 所有测试完成")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务，请先启动 API 服务")
        print("运行: python app.py")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
