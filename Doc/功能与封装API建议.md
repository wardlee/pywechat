# PyWeixin 项目功能分析与 Web API 封装建议

## 项目概述

这是一个基于 **pywinauto** 实现的 Windows 系统下 PC 微信自动化 Python 项目，采用纯 UI 自动化方式（不涉及逆向 Hook 操作），实现了 PC 微信内置的大部分功能。

- **支持版本**: 微信 4.1+
- **操作系统**: Windows 7/10/11
- **Python 版本**: 3.9+
- **支持语言**: 简体中文、English、繁体中文

---

## 一、项目核心功能分类

### 1. 消息管理功能 (Messages)

#### 1.1 消息发送
- ✅ **单人单条消息发送** - `send_messages_to_friend()`
- ✅ **单人多条消息发送** - `send_messages_to_friend()`
- ✅ **多人单条消息发送** - `send_messages_to_friends()`
- ✅ **多人多条消息发送** - `send_messages_to_friends()`
- ✅ **转发消息** - `forward_message()`
- ✅ **群聊 @功能** - 支持 @指定成员、@所有人
- ✅ **拍一拍功能** - 发送消息后拍一拍好友

#### 1.2 消息接收与监听
- ✅ **监听单个聊天窗口** - `Monitor.listen_on_chat()`
- ✅ **检查新消息** - `check_new_message()`
- ✅ **扫描会话列表新消息** - `scan_for_newMessages()`
- ✅ **获取新消息总数** - `get_new_message_num()`

#### 1.3 聊天记录管理
- ✅ **获取聊天记录** - `get_chat_history()`
- ✅ **导出聊天会话** - `dump_chat_sessions()`
- ✅ **转发链接** - `forward_links()`
- ✅ **转发音乐与音频** - `forward_music_and_audio()`
- ✅ **转发小程序** - `forward_MiniPrograms()`

---

### 2. 文件管理功能 (Files)

#### 2.1 文件发送
- ✅ **单人单个文件发送** - `send_files_to_friend()`
- ✅ **单人多个文件发送** - `send_files_to_friend()`
- ✅ **多人单个文件发送** - `send_files_to_friends()`
- ✅ **多人多个文件发送** - `send_files_to_friends()`
- ✅ **转发文件** - `forward_files()`

#### 2.2 文件接收与导出
- ✅ **保存聊天文件到本地** - `save_files()`
- ✅ **保存图片和视频** - `save_media()`
- ✅ **自动下载文件** - 监听时自动保存

---

### 3. 联系人管理功能 (Contacts)

#### 3.1 好友信息获取
- ✅ **获取好友详细信息** - `get_friends_detail()`
  - 昵称、微信号、地区、备注、电话、标签、描述、朋友权限、共同群聊、个性签名、来源
- ✅ **获取企业微信好友信息** - `get_wecom_friends_detail()`
- ✅ **获取服务号信息** - `get_serAcc_info()`
- ✅ **获取公众号信息** - `get_offAcc_info()`
- ✅ **获取群聊信息** - `get_groups_info()`
- ✅ **查看个人信息** - `check_my_info()`

#### 3.2 好友管理
- ✅ **获取共同群聊** - `get_common_groups()`
- ✅ **获取好友个人简介** - `get_friend_profile()`
- ✅ **获取新的朋友列表** - `get_new_friends()`

---

### 4. 好友设置功能 (FriendSettings)

#### 4.1 隐私设置
- ✅ **设置朋友权限** - `set_friend_privacy()`
  - 不让他看我的朋友圈
  - 不看他的朋友圈
- ✅ **设置消息免打扰** - `set_do_not_disturb()`
- ✅ **置顶聊天** - `pin_chat()`
- ✅ **强提醒** - `set_strong_reminder()`

#### 4.2 好友操作
- ✅ **设置备注和标签** - `set_remark_and_tags()`
- ✅ **拍一拍** - `tickle_friend()`
- ✅ **删除好友** - `delete_friend()`
- ✅ **加入黑名单** - `add_to_blacklist()`
- ✅ **投诉好友** - `complain_friend()`

---

### 5. 朋友圈功能 (Moments)

#### 5.1 朋友圈发布
- ✅ **发布朋友圈** - `post_moments()`
  - 支持文本、图片、视频

#### 5.2 朋友圈获取
- ✅ **获取最近朋友圈** - `dump_recent_posts()`
  - 支持按时间筛选（今天、最近三天、最近一周、最近一个月）
- ✅ **导出好友朋友圈** - `dump_friend_posts()`
  - 支持保存图片和视频
- ✅ **点赞和评论好友朋友圈** - `like_friend_posts()`
  - 支持自定义评论函数

---

### 6. 音视频通话功能 (Call)

- ✅ **语音通话** - `voice_call()`
- ✅ **视频通话** - `video_call()`
- ✅ **自动接听** - `auto_answer_call()`

---

### 7. 自动回复功能 (AutoReply)

- ✅ **自动回复好友消息** - `auto_reply_to_friend()`
- ✅ **自动回复群聊消息** - `auto_reply_to_group()`
- ✅ **装饰器方式自动回复** - `@auto_reply_to_friend_decorator`
- ✅ **多线程自动回复** - 支持同时监听多个聊天窗口

---

### 8. 收藏功能 (Collections)

- ✅ **收藏公众号文章** - `collect_offAcc_articles()`
- ✅ **获取收藏链接 URL** - `cardLink_to_url()`

---

### 9. 微信设置功能 (Settings)

- ✅ **更换主题** - `change_theme()`
- ✅ **更换语言** - `change_language()`
- ✅ **修改自动下载文件大小** - `set_auto_download_size()`
- ✅ **修改快捷键** - `set_shortcut_keys()`

---

### 10. 导航与工具功能 (Navigator & Tools)

#### 10.1 界面导航
- ✅ **打开微信主界面** - `open_weixin()`
- ✅ **打开聊天窗口** - `open_dialog_window()`
- ✅ **打开独立聊天窗口** - `open_seperate_dialog_window()`
- ✅ **打开朋友圈** - `open_moments()`
- ✅ **打开通讯录** - `open_contacts()`
- ✅ **打开收藏** - `open_collections()`
- ✅ **打开视频号** - `open_channels()`
- ✅ **打开设置** - `open_settings()`
- ✅ **打开聊天记录** - `open_chat_history()`
- ✅ **打开好友个人简介** - `open_friend_profile()`
- ✅ **打开好友朋友圈** - `open_friend_moments()`

#### 10.2 搜索功能
- ✅ **搜索小程序** - `search_miniprogram()`
- ✅ **搜索公众号** - `search_official_account()`
- ✅ **搜索视频号** - `search_channels()`

#### 10.3 工具功能
- ✅ **判断微信是否运行** - `is_weixin_running()`
- ✅ **获取微信路径** - `where_weixin()`
- ✅ **获取当前 wxid** - `get_current_wxid()`
- ✅ **获取聊天文件夹路径** - `where_chatfile_folder()`
- ✅ **语言检测** - `language_detector()`

---

## 二、适合封装为 Web API 的功能

根据功能的实用性、独立性和 Web 场景需求，以下功能**强烈建议**封装为 Web API：

### 🔥 高优先级 API（核心功能）

#### 1. 消息相关 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/message/send` | POST | 发送消息给好友/群聊 | `friend`, `messages`, `at`, `at_all` |
| `/api/message/forward` | POST | 转发消息给多个好友 | `friends`, `message` |
| `/api/message/history` | GET | 获取聊天记录 | `friend`, `number`, `start_date`, `end_date` |
| `/api/message/new` | GET | 检查新消息 | `duration` |
| `/api/message/listen` | POST | 监听聊天窗口（WebSocket） | `friend`, `duration`, `callback_url` |

**使用场景**：
- 客服系统自动回复
- 消息群发通知
- 聊天记录备份
- 实时消息监控

---

#### 2. 文件相关 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/file/send` | POST | 发送文件给好友/群聊 | `friend`, `files`, `with_messages` |
| `/api/file/save` | POST | 保存聊天文件到服务器 | `friend`, `number`, `target_folder` |
| `/api/file/forward` | POST | 转发文件给多个好友 | `friend`, `others`, `number` |

**使用场景**：
- 文件批量分发
- 聊天文件自动备份
- 文档共享系统

---

#### 3. 联系人相关 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/contacts/friends` | GET | 获取所有好友信息 | `is_json` |
| `/api/contacts/friend/{name}` | GET | 获取指定好友详细信息 | `name` |
| `/api/contacts/groups` | GET | 获取所有群聊信息 | `is_json` |
| `/api/contacts/wecom` | GET | 获取企业微信联系人 | `is_json` |
| `/api/contacts/official` | GET | 获取公众号列表 | `is_json` |
| `/api/contacts/common-groups` | GET | 获取与好友的共同群聊 | `friend` |

**使用场景**：
- CRM 系统集成
- 通讯录同步
- 好友数据分析

---

#### 4. 朋友圈相关 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/moments/post` | POST | 发布朋友圈 | `texts`, `medias` |
| `/api/moments/recent` | GET | 获取最近朋友圈 | `recent` (Today/3days/1week/1month) |
| `/api/moments/friend/{name}` | GET | 获取好友朋友圈 | `name`, `number`, `save_detail` |
| `/api/moments/like` | POST | 点赞/评论好友朋友圈 | `friend`, `number`, `comment` |

**使用场景**：
- 社交媒体管理
- 朋友圈内容分析
- 自动点赞/评论机器人

---

#### 5. 自动回复 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/auto-reply/start` | POST | 启动自动回复 | `friend`, `duration`, `callback_url` |
| `/api/auto-reply/stop` | POST | 停止自动回复 | `session_id` |
| `/api/auto-reply/status` | GET | 查询自动回复状态 | `session_id` |

**使用场景**：
- 智能客服系统
- AI 聊天机器人
- 自动应答服务

---

### ⭐ 中优先级 API（增强功能）

#### 6. 好友设置 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/friend/remark` | PUT | 设置好友备注和标签 | `friend`, `remark`, `tags` |
| `/api/friend/privacy` | PUT | 设置朋友权限 | `friend`, `hide_moments`, `block_moments` |
| `/api/friend/pin` | PUT | 置顶/取消置顶聊天 | `friend`, `pin` |
| `/api/friend/mute` | PUT | 设置消息免打扰 | `friend`, `mute` |
| `/api/friend/tickle` | POST | 拍一拍好友 | `friend` |

**使用场景**：
- 批量好友管理
- 隐私设置自动化

---

#### 7. 音视频通话 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/call/voice` | POST | 发起语音通话 | `friend` |
| `/api/call/video` | POST | 发起视频通话 | `friend` |

**使用场景**：
- 远程呼叫系统
- 自动拨号服务

---

#### 8. 收藏相关 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/collections/articles` | POST | 收藏公众号文章 | `name`, `number` |
| `/api/collections/links` | GET | 获取收藏链接 URL | `number`, `delete` |

**使用场景**：
- 内容聚合平台
- 文章收藏管理

---

### 💡 低优先级 API（辅助功能）

#### 9. 工具类 API

| API 端点 | HTTP 方法 | 功能描述 | 请求参数 |
|---------|----------|---------|---------|
| `/api/tools/status` | GET | 检查微信运行状态 | - |
| `/api/tools/wxid` | GET | 获取当前登录 wxid | - |
| `/api/tools/language` | GET | 获取微信语言版本 | - |

---

## 三、Web API 架构设计建议

### 3.1 技术栈推荐

```
后端框架: FastAPI / Flask
任务队列: Celery + Redis
WebSocket: Socket.IO (用于实时消息推送)
数据库: PostgreSQL / MongoDB
缓存: Redis
认证: JWT Token
文档: Swagger / OpenAPI
```

### 3.2 API 设计原则

#### RESTful 风格
```
GET    /api/contacts/friends      # 获取好友列表
GET    /api/contacts/friends/{id} # 获取指定好友
POST   /api/message/send          # 发送消息
PUT    /api/friend/remark         # 更新备注
DELETE /api/friend/{id}           # 删除好友
```

#### 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 实际数据
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 错误处理
```json
{
  "code": 400,
  "message": "好友不存在",
  "error": "NoSuchFriendError",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

### 3.3 异步任务处理

由于微信 UI 自动化操作耗时较长，建议使用**异步任务队列**：

```python
# 示例：发送消息 API
@app.post("/api/message/send")
async def send_message(request: MessageRequest):
    # 创建异步任务
    task = send_message_task.delay(
        friend=request.friend,
        messages=request.messages
    )
    
    return {
        "code": 200,
        "message": "任务已提交",
        "data": {
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}"
        }
    }

# 查询任务状态
@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    return {
        "code": 200,
        "data": {
            "task_id": task_id,
            "status": task.state,
            "result": task.result
        }
    }
```

---

### 3.4 WebSocket 实时推送

对于消息监听功能，使用 WebSocket 实现实时推送：

```python
# 客户端连接
@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': '连接成功'})

# 启动监听
@socketio.on('start_listen')
def handle_listen(data):
    friend = data['friend']
    duration = data['duration']
    
    # 启动监听任务
    listen_task.delay(friend, duration, session_id=request.sid)

# 推送新消息
def push_new_message(session_id, message):
    socketio.emit('new_message', message, room=session_id)
```

---

### 3.5 安全性考虑

#### 1. 认证与授权
```python
# JWT Token 认证
@app.post("/api/auth/login")
async def login(username: str, password: str):
    # 验证用户
    token = create_jwt_token(username)
    return {"token": token}

# API 需要 Token
@app.get("/api/contacts/friends")
async def get_friends(token: str = Depends(verify_token)):
    # 业务逻辑
    pass
```

#### 2. 速率限制
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/message/send")
@limiter.limit("10/minute")  # 每分钟最多 10 次
async def send_message(request: MessageRequest):
    pass
```

#### 3. 敏感信息脱敏
```python
# 返回好友信息时脱敏
def mask_phone(phone: str):
    return phone[:3] + "****" + phone[-4:]
```

---

## 四、部署架构建议

### 4.1 单机部署（小规模）

```
┌─────────────────────────────────────┐
│         Nginx (反向代理)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      FastAPI (Web API 服务)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Celery Worker (异步任务)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Redis (消息队列)              │
└─────────────────────────────────────┘
```

---

### 4.2 分布式部署（大规模）

```
                  ┌─────────────┐
                  │ Load Balancer│
                  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌───────▼──────┐ ┌──────▼───────┐
│ API Server 1 │ │ API Server 2 │ │ API Server 3 │
└───────┬──────┘ └───────┬──────┘ └──────┬───────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌───────▼──────┐ ┌──────▼───────┐
│  Worker 1    │ │  Worker 2    │ │  Worker 3    │
│ (微信实例1)   │ │ (微信实例2)   │ │ (微信实例3)   │
└───────┬──────┘ └───────┬──────┘ └──────┬───────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                ┌────────▼────────┐
                │  Redis Cluster  │
                └─────────────────┘
```

**注意事项**：
- 每个 Worker 需要独立的 Windows 虚拟机/容器
- 每个 Worker 运行一个微信实例
- 使用任务队列分发请求到不同 Worker

---

## 五、API 使用示例

### 示例 1：发送消息

```bash
curl -X POST "http://api.example.com/api/message/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friend": "张三",
    "messages": ["你好", "这是一条测试消息"],
    "at": [],
    "at_all": false
  }'
```

**响应**：
```json
{
  "code": 200,
  "message": "消息发送成功",
  "data": {
    "task_id": "abc123",
    "status": "completed"
  }
}
```

---

### 示例 2：获取好友列表

```bash
curl -X GET "http://api.example.com/api/contacts/friends" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "昵称": "张三",
      "微信号": "zhangsan123",
      "地区": "北京 海淀",
      "备注": "同事",
      "标签": "工作"
    },
    {
      "昵称": "李四",
      "微信号": "lisi456",
      "地区": "上海 浦东",
      "备注": "朋友",
      "标签": "生活"
    }
  ]
}
```

---

### 示例 3：监听消息（WebSocket）

```javascript
// 客户端代码
const socket = io('ws://api.example.com');

socket.on('connect', () => {
  console.log('已连接到服务器');
  
  // 启动监听
  socket.emit('start_listen', {
    friend: '张三',
    duration: '10min'
  });
});

socket.on('new_message', (data) => {
  console.log('收到新消息:', data);
  // {
  //   "sender": "张三",
  //   "content": "你好",
  //   "type": "文本",
  //   "timestamp": "2024-01-01 12:00:00"
  // }
});
```

---

## 六、注意事项与限制

### 6.1 技术限制

1. **单线程限制**：微信不支持多线程操作，同一微信实例只能串行执行任务
2. **UI 依赖**：需要微信界面可见（可最小化但不能关闭）
3. **速度限制**：UI 自动化速度较慢，不适合高并发场景
4. **版本依赖**：微信更新可能导致 UI 结构变化，需要维护

### 6.2 使用建议

1. **异步处理**：所有耗时操作必须异步化
2. **任务队列**：使用 Celery 等任务队列管理任务
3. **错误重试**：网络波动或 UI 变化时自动重试
4. **日志记录**：详细记录操作日志便于排查问题
5. **监控告警**：监控任务执行状态，异常时及时告警

### 6.3 合规性提醒

⚠️ **重要提示**：
- 本项目仅供学习研究使用
- 请勿用于任何非法商业活动
- 使用时请遵守微信用户协议
- 频繁操作可能导致账号异常

---

## 七、总结

### 推荐封装的核心 API（Top 10）

1. ✅ **消息发送 API** - 最常用，适合通知、客服场景
2. ✅ **消息监听 API** - 实时监控，适合聊天机器人
3. ✅ **获取好友列表 API** - CRM 集成必备
4. ✅ **获取聊天记录 API** - 数据备份与分析
5. ✅ **文件发送 API** - 文档分发场景
6. ✅ **自动回复 API** - 智能客服核心功能
7. ✅ **朋友圈发布 API** - 社交媒体管理
8. ✅ **朋友圈获取 API** - 内容分析与监控
9. ✅ **好友设置 API** - 批量管理好友
10. ✅ **检查新消息 API** - 消息提醒服务

### 技术选型建议

- **后端框架**: FastAPI（高性能、异步支持、自动文档）
- **任务队列**: Celery + Redis（成熟稳定）
- **实时通信**: Socket.IO（WebSocket 封装）
- **数据库**: PostgreSQL（关系型） + MongoDB（日志存储）
- **部署**: Docker + Kubernetes（容器化部署）

---

## 八、后续扩展方向

1. **AI 集成**：接入 ChatGPT/Claude 实现智能对话
2. **数据分析**：聊天记录分析、好友关系图谱
3. **多账号管理**：支持多个微信账号并发操作
4. **Web 管理后台**：可视化管理界面
5. **移动端 App**：iOS/Android 客户端
6. **插件系统**：支持自定义功能扩展

---

**文档版本**: v2.0  
**更新日期**: 2024-01-01  
**作者**: AI Assistant  
**项目地址**: https://github.com/Hello-Mr-Crab/pywechat  
**说明**: 本文档仅针对微信 4.1+ 版本（pyweixin 模块）
