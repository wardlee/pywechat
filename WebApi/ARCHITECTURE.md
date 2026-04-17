# 架构说明

## 三层架构设计

```
┌─────────────────────────────────────────┐
│          API 层 (app.py)                │
│  - HTTP 请求处理                         │
│  - 路由定义                              │
│  - 参数验证                              │
└──────────────┬──────────────────────────┘
               │ 调用
┌──────────────▼──────────────────────────┐
│       业务逻辑层 (service.py)            │
│  - WeChatService (微信业务)              │
│  - MonitorService (监听服务)             │
└──────────────┬──────────────────────────┘
               │ 调用
┌──────────────▼──────────────────────────┐
│       数据访问层 (database.py)           │
│  - Database (数据库操作)                 │
│  - CRUD 操作                             │
└─────────────────────────────────────────┘
```

## 文件职责

### app.py (API 层)
**职责**：处理 HTTP 请求
- 定义 API 路由
- 验证请求参数
- 调用 Service 层
- 返回响应结果
- **不包含**：业务逻辑、数据库操作

**示例**：
```python
@app.post("/api/message/send")
async def send_message(request: SendMessageRequest):
    messages = [request.messages] if isinstance(request.messages, str) else request.messages
    wechat_service.send_message(request.friend_name, messages)
    return {"code": 200, "message": "发送成功"}
```

---

### service.py (业务逻辑层)
**职责**：实现业务逻辑

#### WeChatService
- 发送消息（调用 pyweixin + 保存数据库）
- 获取最新消息（查询 + 标记已读）
- 管理监听列表

#### MonitorService
- 启动/停止监听服务
- 多线程监听多个好友
- 接收消息并保存到数据库

**示例**：
```python
class WeChatService:
    def send_message(self, friend_name: str, messages: List[str]):
        # 1. 调用 pyweixin 发送消息
        Messages.send_messages_to_friend(...)
        # 2. 保存到数据库
        self.db.save_sent_message(friend_name, messages)
```

---

### database.py (数据访问层)
**职责**：数据库操作
- 数据库连接管理
- 表初始化
- CRUD 操作（增删改查）
- **不包含**：业务逻辑

**示例**：
```python
class Database:
    def save_sent_message(self, friend_name: str, messages: List[str]):
        # 纯粹的数据库操作
        with self.get_connection() as conn:
            cursor.execute("INSERT INTO ...")
```

---

## 数据流向

### 发送消息流程
```
1. 用户请求 → app.py (API层)
   POST /api/message/send

2. app.py → service.py (业务层)
   wechat_service.send_message()

3. service.py → pyweixin
   Messages.send_messages_to_friend()

4. service.py → database.py (数据层)
   db.save_sent_message()

5. database.py → SQLite
   INSERT INTO chat_messages
```

### 监听消息流程
```
1. 启动时 → app.py
   启动 MonitorService

2. MonitorService → database.py
   获取监听列表

3. MonitorService → pyweixin
   打开聊天窗口，监听消息

4. 收到新消息 → database.py
   保存到数据库
```

---

## 优势

### 1. 职责清晰
- 每层只做自己的事
- 代码易于理解和维护

### 2. 易于扩展
- 添加新 API → 修改 `app.py`
- 添加新业务逻辑 → 修改 `service.py`
- 添加新数据表 → 修改 `database.py`

### 3. 易于测试
- 可以单独测试每一层
- 可以 Mock 依赖层

### 4. 易于替换
- 想换数据库？只改 `database.py`
- 想换 Web 框架？只改 `app.py`
- 业务逻辑不受影响

---

## 扩展示例

### 添加新功能：获取好友列表

#### 1. 数据层 (database.py)
```python
def get_all_friends(self) -> List[str]:
    """获取所有好友名称"""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT friend_name FROM chat_messages")
        return [row['friend_name'] for row in cursor.fetchall()]
```

#### 2. 业务层 (service.py)
```python
def get_friends_list(self) -> List[str]:
    """获取好友列表"""
    return self.db.get_all_friends()
```

#### 3. API 层 (app.py)
```python
@app.get("/api/friends/list")
async def get_friends():
    """获取好友列表"""
    return wechat_service.get_friends_list()
```

---

## 注意事项

1. **不要跨层调用**
   - ❌ app.py 直接调用 database.py
   - ✅ app.py → service.py → database.py

2. **保持层的纯粹性**
   - database.py 只做数据操作
   - service.py 只做业务逻辑
   - app.py 只做请求处理

3. **依赖注入**
   - Service 层通过构造函数接收 Database 实例
   - 便于测试和替换

---

**设计原则**：单一职责、高内聚、低耦合
