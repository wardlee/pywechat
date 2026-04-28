# 获取历史记录 API 说明

## 接口信息

**接口地址**: `GET /api/message/history`

**功能**: 获取指定好友的聊天历史记录（从数据库查询）

**返回格式**: 纯文本（text/plain），方便直接阅读

---

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| friend_name | string | 是 | - | 好友名称 |
| limit | int | 否 | 20 | 获取记录条数（范围：1-100） |

---

## 响应格式

### 成功响应 (200)

返回纯文本格式：

```txt
当前时间： 26年04月27日 17:30

[12月03日 17:13][小花]： 你好;在吗
[12月03日 17:13][我]： 在的;有什么事
[01月03日 12:13][小花]： 明天见
[01月03日 12:13][我]： 好的
[04月27日 09:10][小花]： 早上好
[04月27日 09:10][我]： 你好
```

### 无记录响应 (200)

```txt
没有记录
```

### 错误响应 (400)

```json
{
  "detail": "friend_name 参数不能为空"
}
```

或

```json
{
  "detail": "limit 参数范围为 1-100"
}
```

---

## 请求示例

### Python

```python
import requests

# 获取默认20条记录
response = requests.get("http://localhost:5200/api/message/history", params={
    "friend_name": "小花"
})
print(response.text)

# 获取10条记录
response = requests.get("http://localhost:5200/api/message/history", params={
    "friend_name": "小花",
    "limit": 10
})
print(response.text)
```

### cURL

```bash
# 获取默认20条记录
curl "http://localhost:5200/api/message/history?friend_name=小花"

# 获取10条记录
curl "http://localhost:5200/api/message/history?friend_name=小花&limit=10"
```

### JavaScript (Fetch)

```javascript
// 获取默认20条记录
fetch('http://localhost:5200/api/message/history?friend_name=小花')
  .then(response => response.text())
  .then(data => console.log(data));

// 获取10条记录
fetch('http://localhost:5200/api/message/history?friend_name=小花&limit=10')
  .then(response => response.text())
  .then(data => console.log(data));
```

---

## 返回格式说明

1. **第一行**: 当前时间（格式：YY年MM月DD日 HH:MM）
2. **第二行**: 空行
3. **后续行**: 聊天记录
   - 格式：`[日期 时间][发送者]： 消息内容`
   - 发送者为 `[我]` 表示自己发送的消息
   - 发送者为 `[好友名称]` 表示好友发送的消息
   - 消息内容保持原样（包含分号等原始格式）
   - 按时间顺序排列（从早到晚）

---

## 注意事项

1. **数据来源**: 该接口从数据库查询历史记录，只能获取监听服务启动后的消息
2. **时间顺序**: 返回的记录按时间顺序排列（最早的在上面）
3. **消息格式**: 数据库中的消息内容原样返回，不做拆分处理
4. **数量限制**: 单次最多获取100条记录
5. **性能**: 查询速度快，不会干扰微信界面
6. **编码**: 返回内容使用 UTF-8 编码

---

## 测试方法

运行测试脚本：

```bash
cd WebApi
python test_history_api.py
```

确保在运行测试前：
1. 微信已登录
2. API 服务已启动（`python app.py`）
3. 监听服务已运行并记录了一些消息
