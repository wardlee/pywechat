# PyWeixin Web API

简单的微信自动化 Web API 服务

## 文件结构

```
WebApi/
├── app.py              # FastAPI 主程序（API 路由层）
├── service.py          # 业务逻辑层（WeChatService + MonitorService）
├── database.py         # 数据访问层（Database）
├── requirements.txt    # 依赖包
├── start.bat          # Windows 启动脚本
├── test_api.py        # API 测试脚本
└── README.md          # 使用说明
```

## 代码架构（三层架构）

### 1. API 层 - app.py
- ✅ HTTP 请求处理
- ✅ 路由定义
- ✅ 参数验证
- ✅ 调用 Service 层

### 2. 业务逻辑层 - service.py
- ✅ **WeChatService** - 微信业务逻辑（发送消息、获取消息等）
- ✅ **MonitorService** - 监听服务（后台监听微信消息）

### 3. 数据访问层 - database.py
- ✅ **Database** - 数据库操作（CRUD）
- ✅ 数据库连接管理
- ✅ 表初始化

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:8000` 启动

### 3. 查看 API 文档

浏览器访问：`http://localhost:8000/docs`

## API 接口

### 1. 发送消息
```bash
POST /api/message/send
{
  "friend_name": "张三",
  "messages": "你好"
}
```

### 2. 获取最新消息
```bash
GET /api/message/latest?friend_name=张三
```

### 3. 获取监听人列表
```bash
GET /api/monitor/list
```

### 4. 设置监听人列表
```bash
POST /api/monitor/set
{
  "friends": ["张三", "李四"]
}
```

## 注意事项

1. 使用前需要先启动微信并登录
2. 需要开启 Windows 讲述人（辅助功能）
3. 监听服务会自动在后台运行
4. 数据库文件 `wechat.db` 会自动创建在当前目录

## 测试示例

```bash
# 发送消息
curl -X POST "http://localhost:8000/api/message/send" \
  -H "Content-Type: application/json" \
  -d '{"friend_name": "张三", "messages": "你好"}'

# 获取最新消息
curl "http://localhost:8000/api/message/latest"

# 设置监听列表
curl -X POST "http://localhost:8000/api/monitor/set" \
  -H "Content-Type: application/json" \
  -d '{"friends": ["张三", "李四"]}'
```
