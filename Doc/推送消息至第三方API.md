# 微信 AI 自动回复 - Hermes 轮询说明

## 目标
系统启动后，后台定时轮询微信消息数据库。  
如果监听好友存在未读消息，则整理最近聊天记录，调用 Hermes 接口生成回复，并自动发送给对应好友。

## 当前实现
- 实现文件：`WebApi/service.py`
- 轮询类：`HermesAutoReplyService`
- 启动位置：`WebApi/app.py`
- 数据库文件：`WebApi/wechat.db`
- 监听配置：`WebApi/data_config.json`

## 执行流程
1. FastAPI 启动时，同时启动 `MonitorService` 和 `HermesAutoReplyService`。
2. `HermesAutoReplyService` 每 30 秒执行一次轮询。
3. 通过 `monitor_service.get_monitor_list()` 获取当前启用监听的好友列表。
4. 逐个好友处理：
   - 从 `data_config.json` 中读取该好友的 `id`
   - 生成 Hermes 会话 ID：`VV_<id>`
   - 调用 `get_chat_history(friend_name, limit, require_unread=True)` 获取最近聊天记录
   - 如果没有未读消息，直接跳过
   - 如果有未读消息，调用 Hermes 接口生成回复
   - 将该好友的未读消息标记为已读
   - 调用 `send_message()` 将回复发回微信

## 会话 ID 规则
Hermes 会话 ID 不再使用 `chat_messages` 表主键。  
当前统一使用 `WebApi/data_config.json` 中配置的好友 `id`：

```json
{
  "id": 1,
  "monitor_friend_name": "佳霖"
}
```

对应的会话 ID 为：

```txt
VV_1
```

要求：
- 每个好友的 `id` 必须唯一
- 如果两个好友使用相同 `id`，Hermes 上下文会串话

## 聊天记录格式
Hermes 接口的 `input` 使用格式化后的纯文本聊天记录。

示例：

```txt
当前时间： 26年04月27日 17:30

[25年12月03日 17:13][小花]： 具体消息内容
[01月03日 12:13][我]： 具体消息内容
[04月27日 09:10][小花]： 具体消息内容
[04月27日 11:10][我]： 具体消息内容
[04月27日 11:10][未读,待回复][小花]： 具体消息内容
```

说明：
- 当前年内的消息格式为：`04月27日 11:10`
- 跨年的消息格式为：`25年12月03日 17:13`
- 未读消息会追加标记：`[未读,待回复]`
- `我` 表示自己发送的消息

## get_chat_history 行为
方法定义：

```python
get_chat_history(friend_name: str, limit: int = 20, require_unread: bool = False) -> str
```

规则：
- `require_unread=False`：返回最近历史记录，包含未读消息
- `require_unread=True`：如果最近记录里没有未读消息，直接返回空字符串 `""`

轮询服务当前使用：

```python
get_chat_history(friend_name, limit, require_unread=True)
```

这样可以直接判断当前好友是否需要调用 Hermes。

## Hermes 接口调用
请求地址：

```txt
http://172.20.19.87:8642/v1/responses
```

请求示例：

```python
import requests

url = "http://172.20.19.87:8642/v1/responses"
api_key = "your_api_key"
session_id = "VV_1"

payload = {
    "model": "hermes-agent",
    "input": "聊天记录文本",
    "conversation": session_id
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-Hermes-Session-Id": session_id
}

resp = requests.post(url, json=payload, headers=headers, timeout=600)
resp_json = resp.json()
text = resp_json["output"][-1]["content"][0]["text"]
```

要求：
- `conversation` 必须传 `VV_<id>`
- `X-Hermes-Session-Id` 也必须传同一个值

## 注意事项
- 根目录下的 `wechat.db` 不再使用
- 所有消息读写统一使用 `WebApi/wechat.db`
- 自动回复只处理监听列表中的好友
- 自动回复成功后，会将该好友的未读消息统一标记为已读
