"""
业务逻辑层
包含微信服务和监听服务
"""
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from database import Database


class WeChatService:
    """微信业务逻辑类"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def send_message(self, friend_name: str, messages: List[str]):
        """发送消息"""
        from pyweixin import Messages
        
        # 发送消息
        Messages.send_messages_to_friend(
            friend=friend_name,
            messages=messages,
            close_weixin=False
        )
        
        # 保存到数据库
        self.db.save_sent_message(friend_name, messages)
    
    def get_latest_messages(self, friend_name: Optional[str] = None) -> List[Dict]:
        """获取最新消息并标记为已读"""
        messages = self.db.get_unread_messages(friend_name)
        
        if messages:
            self.db.mark_as_read(friend_name)
        
        return messages
    
    def get_monitor_list(self) -> List[str]:
        """获取监听人列表"""
        return self.db.get_monitor_list()
    
    def set_monitor_list(self, friends: List[str]):
        """设置监听人列表"""
        self.db.set_monitor_list(friends)


class MonitorService:
    """监听服务类 - 简化版"""
    
    def __init__(self, db: Database):
        self.db = db
        self.monitor_list = []  # 内存中的监听列表
        self.is_running = False
        self.dialog_windows = []
        self.executor = None
    
    def start_monitoring(self):
        """启动/重启监听服务"""
        from pyweixin import Navigator, Tools
        import win32gui, win32con
        
        # 检查微信是否运行
        if not Tools.is_weixin_running():
            print("✗ 微信未运行，请先启动微信")
            return
        
        # 停止旧的监听
        self._cleanup()
        
        # 从数据库加载监听列表到内存
        self.monitor_list = self.db.get_monitor_list()
        
        if not self.monitor_list:
            print("监听列表为空，无需启动监听")
            return
        
        print(f"开始监听: {self.monitor_list}")
        self.is_running = True
        
        # 打开对话窗口 - 每个好友使用独立窗口并最小化
        for friend in self.monitor_list:
            try:
                # 使用独立窗口并最小化，避免窗口合并
                window = Navigator.open_seperate_dialog_window(
                    friend=friend,
                    window_minimize=True,  # 最小化窗口避免干扰
                    close_weixin=True
                )
                self.dialog_windows.append((window, friend))
                print(f"✓ 已打开 {friend} 的独立窗口")
            except Exception as e:
                print(f"✗ 无法打开 {friend} 的窗口: {e}")
        
        # 启动多线程监听
        if self.dialog_windows:
            self.executor = ThreadPoolExecutor(max_workers=len(self.dialog_windows))
            for window, friend in self.dialog_windows:
                self.executor.submit(self.monitor_friend, window, friend)
    
    def monitor_friend(self, dialog_window, friend_name):
        """监听单个好友的消息（保存自己和好友的所有消息）"""
        from pyweixin import Tools
        from pyweixin.Uielements import Lists
        
        Lists_instance = Lists()
        last_message_id = 0
        
        print(f"✓ 开始监听: {friend_name}")
        
        while self.is_running:
            try:
                # 获取聊天列表
                chatList = dialog_window.child_window(**Lists_instance.FriendChatList)
                
                if chatList.children(control_type='ListItem'):
                    new_message = chatList.children(control_type='ListItem')[-1]
                    runtime_id = new_message.element_info.runtime_id
                    
                    # 检查是否是新消息
                    if runtime_id != last_message_id:
                        # 判断消息是谁发的
                        is_mine = Tools.is_my_bubble(dialog_window, new_message)
                        content = new_message.window_text()
                        
                        if is_mine:
                            # 自己发送的消息
                            print(f"[{friend_name}] 我发送: {content}")
                            self.db.save_sent_message(friend_name, [content])
                        else:
                            # 好友发送的消息
                            print(f"[{friend_name}] 收到消息: {content}")
                            self.db.save_received_message(friend_name, content)
                        
                        last_message_id = runtime_id
                
                time.sleep(1)  # 每秒检查一次
                
            except Exception as e:
                if self.is_running:  # 只在运行时报错
                    print(f"✗ 监听 {friend_name} 时出错: {e}")
                    time.sleep(2)
                else:
                    break
    
    def _cleanup(self):
        """清理资源"""
        self.is_running = False
        
        # 关闭所有窗口
        for item in self.dialog_windows:
            try:
                # item 是 (window, friend_name) 元组
                if isinstance(item, tuple):
                    window, _ = item
                else:
                    window = item
                window.close()
            except:
                pass
        self.dialog_windows.clear()
        
        # 停止线程池
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
    