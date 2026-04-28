# 微信 AI 自动回复 - 消息轮询模块需求文档

##  业务背景与目标
我们需要开发一个独立的后台任务类（Worker Class）。该类的唯一职责是：**定时主动轮询数据库**，发现未读的微信新消息后，将其提取出来，调用 Hermes 大模型接口获取回复，并更新数据库状态。


##  核心业务流程 (执行逻辑)

1. **定时触发：** 系统启动后，每隔 **30 秒**执行一次数据库查询。
2. **抓取未处理消息：** 
   1. monitor_service.get_monitor_list()方法获取好友监听列表
   2. 查询`chat_messages`表中指定的`friend_name` 且 `is_read = false` 的记录, 以及20条最近的聊天记录。
   3. 将查出的记录按好友分组好, 循环调用API接口.
3. **消息处理与 AI 的API调用：**
   * 将 `received_messages` 发送给 Hermes 接口（通过 Web API 调用）。
   * 接口调用时，**必须将记录的 `VV_`+`id`值 作为 `X-Hermes-Session-Id` 传入**，以保证 AI 上下文的连续性。
4. **状态回写：** * 获取到 AI 的回复文本后，将当前记录的 `is_read` 状态更新为 `true`，防止下个 30 秒周期重复处理。。


## 最新消息及最近聊天记录的格式
```txt

```

##  核心代码逻辑参考
```python
import requests

url = "http://172.20.19.87:8642/v1/responses"
api_key = "2cf7f73cd69db3d3961d8ad1ccd976a33e5b35bd5e9d95e4404219a1b87127fa"

data = {
    "model": "hermes-agent",
    "input": "XXXXXXX消息内容 ",
    "conversation": "VV_00"
}
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

resp = requests.post(url, json=data, headers=headers)
print(resp.json())
resp_json = resp.json()
text = resp_json["output"][-1]["content"][0]["text"]
print(text)

```