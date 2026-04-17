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
    """监听服务类"""
    
    def __init__(self, db: Database):
        self.db = db
        self.is_running = False
        self.dialog_windows = []
        self.executor = None
        self.current_friends = []
    
    def monitor_friend(self, dialog_window, friend_name):
        """监听单个好友的消息"""
        try:
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
                            # 判断是否是好友发的（不是自己发的）
                            is_mine = Tools.is_my_bubble(dialog_window, new_message)
                            
                            if not is_mine:
                                content = new_message.window_text()
                                print(f"[{friend_name}] 收到消息: {content}")
                                
                                # 保存到数据库
                                self.db.save_received_message(friend_name, content)
                            
                            last_message_id = runtime_id
                    
                    time.sleep(1)  # 每秒检查一次
                    
                except Exception as e:
                    print(f"✗ 监听 {friend_name} 时出错: {e}")
                    time.sleep(2)
            
        except Exception as e:
            print(f"✗ 无法监听 {friend_name}: {e}")
    
    def start(self):
        """启动监听服务"""
        try:
            from pyweixin import Navigator, Tools
            
            # 检查微信是否运行
            if not Tools.is_weixin_running():
                print("✗ 微信未运行，请先启动微信")
                return
            
            self.is_running = True
            
            while self.is_running:
                # 获取监听列表
                friends = self.db.get_monitor_list()
                
                # 如果监听列表变化，重启监听
                if friends != self.current_friends:
                    print(f"监听列表更新: {friends}")
                    
                    # 关闭旧窗口
                    for window in self.dialog_windows:
                        try:
                            window.close()
                        except:
                            pass
                    self.dialog_windows.clear()
                    
                    # 停止旧的线程池
                    if self.executor:
                        self.executor.shutdown(wait=False)
                    
                    # 打开新窗口
                    if friends:
                        for friend in friends:
                            try:
                                window = Navigator.open_seperate_dialog_window(
                                    friend=friend,
                                    window_minimize=True,
                                    close_weixin=True
                                )
                                self.dialog_windows.append(window)
                            except Exception as e:
                                print(f"✗ 无法打开 {friend} 的窗口: {e}")
                        
                        # 启动多线程监听
                        if self.dialog_windows:
                            self.executor = ThreadPoolExecutor(max_workers=len(self.dialog_windows))
                            for window, friend in zip(self.dialog_windows, friends):
                                self.executor.submit(self.monitor_friend, window, friend)
                    
                    self.current_friends = friends
                
                # 每 5 秒检查一次监听列表是否变化
                time.sleep(5)
        
        except Exception as e:
            print(f"✗ 监听服务启动失败: {e}")
            self.is_running = False
    
    def restart(self):
        """重启监听服务（通过清空 current_friends 触发重新加载）"""
        print("正在重启监听服务...")
        self.current_friends = []
    
    def stop(self):
        """停止监听服务"""
        print("正在停止监听服务...")
        self.is_running = False
        
        # 关闭所有窗口
        for window in self.dialog_windows:
            try:
                window.close()
            except:
                pass
        
        # 停止线程池
        if self.executor:
            self.executor.shutdown(wait=True)
        
        print("✓ 监听服务已停止")
