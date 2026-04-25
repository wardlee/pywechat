

import requests
import sys
import json

API_BASE_URL = "http://localhost:5200"


def getNewData(userName=""):
    """获取新消息"""
    try:
        url = f"{API_BASE_URL}/api/message/latest"
        params = {"friend_name": userName} if userName else {}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        messages = response.json()
        
        # 格式化输出
        if messages:
            for msg in messages:
                print(f"[{msg['friend_name']}] {msg['content']} ({msg['timestamp']})")
        else:
            print("无新消息")
        
        return messages
        
    except Exception as e:
        print(f"获取消息失败: {e}")
        return []


def sendMsg(toUser, msg):
    """发送消息"""
    try:
        url = f"{API_BASE_URL}/api/message/send"
        data = {
            "friend_name": toUser,
            "messages": msg
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        print(f"消息已发送给 {toUser}")
        
    except Exception as e:
        print(f"发送消息失败: {e}")


def getMonitorList():
    """获取监听人列表"""
    try:
        url = f"{API_BASE_URL}/api/monitor/list"
        
        response = requests.get(url)
        response.raise_for_status()
        
        friends = response.json()
        
        if friends:
            print("当前监听人列表:")
            for friend in friends:
                print(f"  - {friend}")
        else:
            print("监听列表为空")
        
        return friends
        
    except Exception as e:
        print(f"获取监听列表失败: {e}")
        return []


def setMonitorList(*friends):
    """设置监听人列表"""
    try:
        url = f"{API_BASE_URL}/api/monitor/set"
        data = {
            "friends": list(friends)
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        if friends:
            print(f"监听列表已更新: {', '.join(friends)}")
        else:
            print("监听列表已清空")
        
    except Exception as e:
        print(f"设置监听列表失败: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  获取新消息: python wechat.py getNewData [好友名称]")
        print("  发送消息: python wechat.py sendMsg <好友名称> <消息内容>")
        print("  获取监听列表: python wechat.py getMonitorList")
        print("  设置监听列表: python wechat.py setMonitorList <好友1> [好友2] [好友3] ...")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "getNewData":
        userName = sys.argv[2] if len(sys.argv) > 2 else ""
        getNewData(userName)
    
    elif command == "sendMsg":
        if len(sys.argv) < 4:
            print("错误: 缺少参数")
            print("用法: python wechat.py sendMsg <好友名称> <消息内容>")
            sys.exit(1)
        
        toUser = sys.argv[2]
        msg = sys.argv[3]
        sendMsg(toUser, msg)
    
    elif command == "getMonitorList":
        getMonitorList()
    
    elif command == "setMonitorList":
        if len(sys.argv) < 3:
            print("错误: 缺少参数")
            print("用法: python wechat.py setMonitorList <好友1> [好友2] [好友3] ...")
            print("提示: 不提供好友名称将清空监听列表")
            sys.exit(1)
        
        friends = sys.argv[2:]
        setMonitorList(*friends)
    
    else:
        print(f"错误: 未知命令 '{command}'")
        print("支持的命令: getNewData, sendMsg, getMonitorList, setMonitorList")
        sys.exit(1)
    