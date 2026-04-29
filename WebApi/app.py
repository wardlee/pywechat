"""
PyWeixin Web API 主程序
只负责 API 路由和请求处理
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径，以便导入 pyweixin 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import threading
from typing import Union, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 导入数据库
from database import Database
# 导入服务层
from service import WeChatService, MonitorService, HermesAutoReplyService

# ==================== 配置 ====================
app = FastAPI(title="PyWeixin API", version="1.0.0")

# 全局实例
db = Database(str(Path(__file__).with_name("wechat.db")))
wechat_service = WeChatService(db)
monitor_service = None
hermes_auto_reply_service = None

# ==================== 请求模型 ====================

class SendMessageRequest(BaseModel):
    friend_name: str
    messages: Union[str, List[str]]


# ==================== API 接口 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    print("✓ 数据库初始化完成")
    
    # 启动监听服务（传入配置文件路径）
    global monitor_service, hermes_auto_reply_service
    config_path = os.path.join(os.path.dirname(__file__), "data_config.json")
    monitor_service = MonitorService(db, config_path)
    threading.Thread(target=monitor_service.start_monitoring, daemon=True).start()
    print("✓ 监听服务已启动（基于 JSON 配置）")

    hermes_auto_reply_service = HermesAutoReplyService(
        db=db,
        wechat_service=wechat_service,
        monitor_service=monitor_service,
    )
    hermes_auto_reply_service.start()


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "PyWeixin Web API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/message/send")
async def send_message(request: SendMessageRequest):
    """
    发送消息
    支持单条消息（字符串）或多条消息（数组）
    """
    try:
        # 统一转换为列表
        messages = [request.messages] if isinstance(request.messages, str) else request.messages
        
        # 调用业务逻辑
        wechat_service.send_message(request.friend_name, messages)
        
        return {
            "code": 200,
            "message": "发送成功"
        }
        
    except Exception as e:
        error_msg = str(e)
        if "NoSuchFriendError" in error_msg or "好友" in error_msg:
            raise HTTPException(status_code=400, detail="好友不存在")
        raise HTTPException(status_code=500, detail=f"发送失败: {error_msg}")


@app.get("/api/message/latest")
async def get_latest_messages(friend_name: str = None):
    """
    获取最新消息
    如果指定 friend_name，只返回该好友的未读消息
    否则返回所有未读消息
    """
    return wechat_service.get_latest_messages(friend_name)


@app.get("/api/message/history")
async def get_chat_history(friend_name: str, limit: int = 20):
    """
    获取聊天历史记录
    参数：
    - friend_name: 好友名称（必填）
    - limit: 获取记录条数，默认20条
    
    返回纯文本格式，方便直接阅读
    """
    if not friend_name:
        raise HTTPException(status_code=400, detail="friend_name 参数不能为空")
    
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit 参数范围为 1-100")
    
    history_text = wechat_service.get_chat_history(friend_name, limit)
    
    # 返回纯文本
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=history_text)


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("PyWeixin Web API 启动中...")
    print("=" * 50)
    # 使用 5200 端口，避免 Windows 保留端口冲突
    uvicorn.run(app, host="0.0.0.0", port=5200)

