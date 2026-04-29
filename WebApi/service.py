"""
业务逻辑层
包含微信服务和监听服务
"""
import time
import json
import os
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

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
    
    def get_chat_history(self, friend_name: str, limit: int = 20, require_unread: bool = False) -> str:
        """获取聊天历史记录，返回格式化的文本"""
        records = self.db.get_chat_history(friend_name, limit)
        
        if not records:
            return ""

        if require_unread and not any(record.get('is_read') == 0 for record in records):
            return ""
        
        # 构建返回文本
        current_time = datetime.now().strftime("%y年%m月%d日 %H:%M")
        lines = [
            f"当前时间： {current_time}",
            ""
        ]
        
        current_year = datetime.now().year

        def format_time(time_text: str) -> str:
            if not time_text:
                return ""

            try:
                dt = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")
                if dt.year != current_year:
                    return dt.strftime("%y年%m月%d日 %H:%M")
                return dt.strftime("%m月%d日 %H:%M")
            except Exception:
                return time_text

        # 按时间倒序处理记录（最新的在下面）
        for record in reversed(records):
            received_time = record.get('received_time', '')
            sent_time = record.get('sent_time', '')
            received_msgs = record.get('received_messages', '')
            sent_msgs = record.get('sent_messages', '')
            is_read = record.get('is_read', 1)  # 默认已读

            entries = []
            if received_msgs:
                received_label = f"[{format_time(received_time)}][{friend_name}]： {received_msgs}"
                if is_read == 0:
                    received_label = f"[{format_time(received_time)}][未读,待回复][{friend_name}]： {received_msgs}"
                entries.append((received_time or "", 0, received_label))

            if sent_msgs:
                entries.append((sent_time or "", 1, f"[{format_time(sent_time)}][我]： {sent_msgs}"))

            # 同一条记录中优先按时间排序，时间相同时先展示收到的消息
            entries.sort(key=lambda item: (item[0], item[1]))
            for _, _, text in entries:
                lines.append(text)
        
        return "\n".join(lines)


class HermesAutoReplyService:
    """定时轮询未读消息并调用 Hermes 自动回复"""

    def __init__(
        self,
        db: Database,
        wechat_service: WeChatService,
        monitor_service: "MonitorService",
        interval_seconds: int = 10, # 间隔30秒查一次最新消息
        api_url: str = "http://172.20.19.87:8642/v1/responses",
        api_key: str = "2cf7f73cd69db3d3961d8ad1ccd976a33e5b35bd5e9d95e4404219a1b87127fa",
        model: str = "hermes-agent",
        history_limit: int = 10, # 历史记录数
        request_timeout: int = 600, # 超时
    ):
        self.db = db
        self.wechat_service = wechat_service
        self.monitor_service = monitor_service
        self.interval_seconds = interval_seconds
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.history_limit = history_limit
        self.request_timeout = request_timeout
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """启动轮询线程"""
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="hermes-auto-reply")
        self._thread.start()
        print(f"✓ Hermes 自动回复轮询已启动，间隔 {self.interval_seconds} 秒")

    def stop(self):
        """停止轮询线程"""
        self._stop_event.set()

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.process_once()
            except Exception as e:
                print(f"✗ Hermes 自动回复轮询异常: {e}")

            self._stop_event.wait(self.interval_seconds)

    def process_once(self):
        """执行一次轮询处理"""
        for friend_name in self.monitor_service.get_monitor_list():
            self._reply_friend(friend_name)

    def _reply_friend(self, friend_name: str):
        session_id = self._get_session_id(friend_name)
        if not session_id:
            return

        history_text = self.wechat_service.get_chat_history(
            friend_name,
            self.history_limit,
            require_unread=True,
        )
        if not history_text:
            return

        try:
            reply_text = self._call_hermes_api(history_text, session_id)
            self.db.mark_as_read(friend_name)
            self.wechat_service.send_message(friend_name, [reply_text])
            print(f"✓ Hermes 已回复 [{friend_name}]")
        except Exception as e:
            print(f"✗ Hermes 自动回复失败 [{friend_name}]: {e}")

    def _get_session_id(self, friend_name: str) -> str:
        config = self.monitor_service._load_config_from_json()
        for item in config:
            if item.get("monitor_friend_name") == friend_name:
                friend_id = item.get("id")
                return f"VV_{friend_id}" if friend_id is not None else ""
        return ""

    def _call_hermes_api(self, input_text: str, session_id: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Hermes-Session-Id": session_id,
        }
        payload = {
            "model": self.model,
            "input": input_text,
            "conversation": session_id,
        }

        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=self.request_timeout,
        )
        response.raise_for_status()

        resp_json = response.json()
        output = resp_json.get("output") or []
        if not output:
            raise ValueError(f"响应缺少 output: {resp_json}")

        last_item = output[-1]
        content = last_item.get("content") or []
        if not content:
            raise ValueError(f"响应缺少 content: {resp_json}")

        text = content[0].get("text", "").strip()
        if not text:
            raise ValueError(f"响应缺少 text: {resp_json}")

        return text


class MonitorService:
    """监听服务类 - 基于 JSON 配置"""
    
    def __init__(self, db: Database, config_path: str = "data_config.json"):
        self.db = db
        self.config_path = config_path
        self.monitor_list = []  # 内存中的监听列表
        self.is_running = False
        self.dialog_windows = []
        self.executor = None
        self.last_config_mtime = 0  # 配置文件最后修改时间
        self.config_check_interval = 5  # 每5秒检查一次配置文件
    
    def _load_config_from_json(self) -> List[Dict]:
        """从 JSON 文件加载配置"""
        try:
            if not os.path.exists(self.config_path):
                print(f"✗ 配置文件不存在: {self.config_path}")
                return []
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config if isinstance(config, list) else []
        except Exception as e:
            print(f"✗ 读取配置文件失败: {e}")
            return []
    
    def _save_config_to_json(self, config: List[Dict]):
        """保存配置到 JSON 文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"✗ 保存配置文件失败: {e}")
    
    def _get_active_monitor_list(self) -> List[str]:
        """获取需要监听的好友列表（is_monitoring=true）"""
        config = self._load_config_from_json()
        active_friends = []
        
        for item in config:
            if item.get('is_monitoring', False):
                friend_name = item.get('monitor_friend_name', '')
                if friend_name:
                    active_friends.append(friend_name)
        
        return active_friends
    
    def get_monitor_list(self) -> List[str]:
        """获取当前内存中的监听列表（公开方法供外部调用）"""
        return self.monitor_list.copy()  # 返回副本，避免外部修改
    
    def _handle_first_monitor(self, friend_name: str):
        """处理首次监听逻辑"""
        config = self._load_config_from_json()
        
        for item in config:
            if item.get('monitor_friend_name') == friend_name and item.get('is_first_monitor', False):
                print(f"⚡ 首次监听 {friend_name}，执行特殊逻辑...")
                
                # TODO: 在这里添加首次监听的特殊代码逻辑
                # 例如：发送欢迎消息、初始化数据等
                
                # 执行完成后，设置 is_first_monitor 为 false
                item['is_first_monitor'] = False
                self._save_config_to_json(config)
                print(f"✓ {friend_name} 首次监听逻辑已执行，标记已更新")
                break
    
    def _check_config_changed(self) -> bool:
        """检查配置文件是否发生变化"""
        try:
            if not os.path.exists(self.config_path):
                return False
            
            current_mtime = os.path.getmtime(self.config_path)
            
            if self.last_config_mtime == 0:
                # 首次检查，记录时间
                self.last_config_mtime = current_mtime
                return False
            
            if current_mtime != self.last_config_mtime:
                self.last_config_mtime = current_mtime
                return True
            
            return False
        except Exception as e:
            print(f"✗ 检查配置文件变化失败: {e}")
            return False
    
    def start_monitoring(self):
        """启动/重启监听服务"""
        from pyweixin import Navigator, Tools
        import win32gui, win32con
        
        # 检查微信是否运行
        if not Tools.is_weixin_running():
            print("✗ 微信未运行，请先启动微信")
            return
        
        # 如果是首次启动且有旧资源，先清理
        # 注意：重启场景下，_monitor_config_changes 已经清理过了
        if self.is_running or self.dialog_windows or self.executor:
            print("检测到旧的监听服务，先进行清理...")
            self._cleanup()
            # 额外等待确保资源完全释放
            time.sleep(1)
        
        # 从 JSON 加载监听列表到内存
        self.monitor_list = self._get_active_monitor_list()
        
        if not self.monitor_list:
            print("监听列表为空，无需启动监听")
            return
        
        print(f"开始监听: {self.monitor_list}")
        self.is_running = True
        
        # 打开对话窗口 - 每个好友使用独立窗口并最小化
        for friend in self.monitor_list:
            try:
                # 处理首次监听逻辑
                self._handle_first_monitor(friend)
                
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
            self.executor = ThreadPoolExecutor(max_workers=len(self.dialog_windows) + 1)
            
            # 启动消息监听线程
            for window, friend in self.dialog_windows:
                self.executor.submit(self.monitor_friend, window, friend)
            
            # 启动配置文件监控线程
            self.executor.submit(self._monitor_config_changes)
            
            print(f"✓ 监听服务启动完成，共监听 {len(self.dialog_windows)} 个好友")
    
    def _monitor_config_changes(self):
        """监控配置文件变化，自动重启监听服务"""
        print("✓ 配置文件监控已启动")
        
        while self.is_running:
            try:
                time.sleep(self.config_check_interval)
                
                if self._check_config_changed():
                    print("⚡ 检测到配置文件变化，重新加载监听列表...")
                    
                    # 获取新的监听列表
                    new_monitor_list = self._get_active_monitor_list()
                    
                    # 比较是否发生变化
                    if set(new_monitor_list) != set(self.monitor_list):
                        print(f"监听列表已变化: {self.monitor_list} -> {new_monitor_list}")
                        print("正在重启监听服务...")
                        
                        # 设置停止标志
                        self.is_running = False
                        
                        # 关闭所有对话窗口（不等待线程池）
                        if self.dialog_windows:
                            print(f"正在关闭 {len(self.dialog_windows)} 个对话窗口...")
                            for item in self.dialog_windows:
                                try:
                                    if isinstance(item, tuple):
                                        window, friend_name = item
                                        print(f"  关闭 {friend_name} 的窗口...")
                                    else:
                                        window = item
                                    
                                    if window and hasattr(window, 'close'):
                                        window.close()
                                except Exception as e:
                                    print(f"  关闭窗口时出错: {e}")
                            
                            self.dialog_windows.clear()
                            print("✓ 所有窗口已关闭")
                        
                        # 等待其他监听线程退出
                        print("等待监听线程退出...")
                        time.sleep(2)
                        
                        # 停止线程池（不等待，因为当前线程也在其中）
                        if self.executor:
                            self.executor.shutdown(wait=False)
                            self.executor = None
                            print("✓ 线程池已停止")
                        
                        print("✓ 旧监听服务已停止")
                        
                        # 等待一下确保资源释放
                        time.sleep(1)
                        
                        # 重新启动监听服务
                        self.start_monitoring()
                        break  # 退出当前监控线程，新的监控线程会在 start_monitoring 中启动
                    else:
                        print("监听列表未变化，继续监听")
                
            except Exception as e:
                if self.is_running:
                    print(f"✗ 监控配置文件时出错: {e}")
                    time.sleep(2)
                else:
                    break
    
    def monitor_friend(self, dialog_window, friend_name):
        """监听单个好友的消息（保存自己和好友的所有消息）"""
        from pyweixin import Tools
        from pyweixin.Uielements import Lists
        import win32gui, win32con
        
        Lists_instance = Lists()
        last_message_id = None  # 初始化为 None，表示首次启动
        
        print(f"✓ 开始监听: {friend_name}")
        
        while self.is_running:
            try:
                # 获取聊天列表
                chatList = dialog_window.child_window(**Lists_instance.FriendChatList)
                
                if chatList.children(control_type='ListItem'):
                    new_message = chatList.children(control_type='ListItem')[-1]
                    runtime_id = new_message.element_info.runtime_id
                    
                    # 首次启动：只记录 ID，不保存消息
                    if last_message_id is None:
                        last_message_id = runtime_id
                        print(f"[{friend_name}] 初始化完成，开始监听新消息")
                        continue
                    
                    # 检查是否是新消息
                    if runtime_id != last_message_id:
                        content = new_message.window_text()

                        # 过滤 与聊天无关的 关键字
                        if content in ["语音通话通话时长","视频通话通话时长"] or content.strip() == "视频通话已取消" or content.strip() == "语音通话已取消"or content.strip() == "图片"or content.strip() == "动画表情" :
                            continue
                        
                        # 临时恢复窗口以进行判断
                        dialog_window.restore()
                        
                        # 判断消息是谁发的
                        is_mine = Tools.is_my_bubble(dialog_window, new_message)
                        
                        # 判断完成后立即最小化
                        win32gui.SendMessage(dialog_window.handle, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
                        
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
        """清理资源（用于正常关闭，非重启场景）"""
        print("开始清理监听资源...")
        
        # 先设置停止标志，让所有线程退出循环
        self.is_running = False
        
        # 关闭所有窗口
        if self.dialog_windows:
            print(f"正在关闭 {len(self.dialog_windows)} 个对话窗口...")
            for item in self.dialog_windows:
                try:
                    # item 是 (window, friend_name) 元组
                    if isinstance(item, tuple):
                        window, friend_name = item
                        print(f"  关闭 {friend_name} 的窗口...")
                    else:
                        window = item
                    
                    # 尝试关闭窗口
                    if window and hasattr(window, 'close'):
                        window.close()
                except Exception as e:
                    print(f"  关闭窗口时出错: {e}")
            
            self.dialog_windows.clear()
            print("✓ 所有窗口已关闭")
        
        # 等待线程退出
        print("等待线程退出...")
        time.sleep(2)
        
        # 停止线程池
        if self.executor:
            print("正在停止线程池...")
            self.executor.shutdown(wait=False)  # 不等待，避免死锁
            self.executor = None
            print("✓ 线程池已停止")
        
        print("✓ 资源清理完成")
