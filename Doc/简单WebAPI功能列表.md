# 简单 Web API 功能需求

## 数据库设计（SQLite）

### 表1：聊天消息表 `chat_messages`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| friend_name | TEXT | 微信好友名称 |
| received_messages | TEXT | 好友发送的消息（多条用 `;` 分隔） |
| sent_messages | TEXT | 我回复的消息（多条用 `;` 分隔） |
| is_read | INTEGER | 是否已获取（0=未读，1=已读） |
| received_time | TEXT | 好友发送消息的时间 |
| remark | TEXT | 备注 |

**存储规则**：
- 好友连续发送多条消息，都追加到 `received_messages` 字段，用 `;` 分隔
- 我回复的多条消息，都追加到 `sent_messages` 字段，用 `;` 分隔

---

### 表2：监听人列表 `monitor_list`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| friend | TEXT | 监听的好友名称（多个用 `;` 分隔） |


---

## API 接口需求

### 1. 发送消息

**接口**: `POST /api/message/send`

**参数**:
```json
{
  "friend_name": "张三",
  "messages": "你好"  // 单条消息
}
```
或
```json
{
  "friend_name": "张三",
  "messages": ["你好", "在吗", "有空吗"]  // 多条消息
}
```

**说明**：
- `messages` 可以是字符串（单条）或数组（多条）
- 发送成功后，将消息追加到数据库 `sent_messages` 字段

**响应示例**:
```json
{
  "code": 200,
  "message": "发送成功"
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "异常。。。"
}
```

---

### 2. 获取最新消息

**接口**: `GET /api/message/latest`

**参数**:
- `friend_name`（可选）：指定好友名称，不传则返回所有未读消息

**功能**：
1. 查询数据库中 `is_read = 0` 的记录
2. 返回这些记录
3. 将这些记录的 `is_read` 设置为 `1`

**响应示例**:
```json
[
    {
      "friend_name": "张三",
      "received_messages": "你好;在吗;有空吗",
      "received_time": "2024-01-01 12:00:00"
    }
]
```

---

### 3. 获取监听人列表

**接口**: `GET /api/monitor/list`

**功能**：
- 从 `monitor_list` 表读取 `friend` 字段

**响应示例**:
```json
{
  "friends": ["张三", "李四", "王五"]
}
```

---

### 4. 设置监听人列表

**接口**: `POST /api/monitor/set`

**参数**:
```json
{
  "friends": ["张三", "李四", "王五"]
}
```

**功能**：
- 更新 `monitor_list` 表的 `friend` 字段（多个好友用 `;` 分隔存储）
- 重启后台监听服务

**响应示例**:
```json
{
  "code": 200,
  "message": "监听列表设置成功"
}
```

---

## 后台监听服务

**功能**：
1. 读取 `monitor_list` 表的 `friend` 字段
2. 为每个好友启动监听
3. 收到新消息时：
   - 追加到数据库 `received_messages` 字段
   - 设置 `is_read = 0`
   - 更新 `received_time`

---
