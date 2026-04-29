

import requests
import sys
import json

API_BASE_URL = "http://localhost:5200"


def getHistoryData(userName, limit=20):
    """获取历史消息"""
    try:
        url = f"{API_BASE_URL}/api/message/history"
        params = {
            "friend_name": userName,
            "limit": limit,
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        history_text = response.text.strip()
        print(history_text if history_text else "没有记录")
        return history_text
        
    except Exception as e:
        print(f"获取历史消息失败: {e}")
        return ""


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  获取历史消息: python wechat.py getHistoryData <好友名称> [条数]")
        print("  发送消息: python wechat.py sendMsg <好友名称> <消息内容>")
        print("  获取监听列表: python wechat.py getMonitorList")
        print("  设置监听列表: python wechat.py setMonitorList <好友1> [好友2] [好友3] ...")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "getHistoryData":
        if len(sys.argv) < 3:
            print("错误: 缺少参数")
            print("用法: python wechat.py getHistoryData <好友名称> [条数]")
            sys.exit(1)

        userName = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        getHistoryData(userName, limit)
    
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
    
    else:
        print(f"错误: 未知命令 '{command}'")
        print("支持的命令: getHistoryData, sendMsg, getMonitorList, setMonitorList")
        sys.exit(1)
    
