"""
数据库操作
只负责数据的增删改查
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional


class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path(__file__).with_name("wechat.db"))
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建聊天消息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    friend_name TEXT NOT NULL,
                    received_messages TEXT,
                    sent_messages TEXT,
                    is_read INTEGER DEFAULT 0,
                    received_time TEXT,
                    sent_time TEXT,
                    remark TEXT
                )
            """)
            
            # 检查并添加 sent_time 列（用于已存在的数据库）
            cursor.execute("PRAGMA table_info(chat_messages)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'sent_time' not in columns:
                cursor.execute("ALTER TABLE chat_messages ADD COLUMN sent_time TEXT")

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_friend_id
                ON chat_messages(friend_name, id DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_friend_unread
                ON chat_messages(friend_name, is_read, id DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_unread
                ON chat_messages(is_read, id DESC)
            """)
            
            conn.commit()
    
    # ==================== 消息相关 ====================
    
    def save_sent_message(self, friend_name: str, messages: List[str]):
        """保存发送的消息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 优先合并到该好友最新一条记录，避免自动回复/连续发送拆成大量行。
            cursor.execute(
                """
                SELECT id, sent_messages
                FROM chat_messages
                WHERE friend_name = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (friend_name,)
            )
            row = cursor.fetchone()
            
            # 合并消息
            new_messages = " ; ".join(messages)
            
            if row:
                # 追加到现有记录
                existing = row['sent_messages'] or ""
                updated = f"{existing} ; {new_messages}" if existing else new_messages
                cursor.execute(
                    "UPDATE chat_messages SET sent_messages = ?, sent_time = ? WHERE id = ?",
                    (updated, current_time, row['id'])
                )
            else:
                # 创建新记录
                cursor.execute(
                    """
                    INSERT INTO chat_messages (friend_name, sent_messages, sent_time, is_read)
                    VALUES (?, ?, ?, 1)
                    """,
                    (friend_name, new_messages, current_time)
                )
            
            conn.commit()
    
    def save_received_message(self, friend_name: str, message: str):
        """保存接收到的消息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 连续好友消息合并到同一条记录：
            # 1. 优先合并未读记录；
            # 2. 如果最新记录还没有我方回复，即使已读也继续合并。
            cursor.execute(
                """
                SELECT id, received_messages
                FROM chat_messages
                WHERE friend_name = ?
                  AND (is_read = 0 OR (sent_messages IS NULL OR sent_messages = ''))
                ORDER BY id DESC
                LIMIT 1
                """,
                (friend_name,)
            )
            row = cursor.fetchone()
            
            if row:
                # 追加到现有记录
                existing = row['received_messages'] or ""
                updated = f"{existing} ; {message}" if existing else message
                cursor.execute(
                    """
                    UPDATE chat_messages 
                    SET received_messages = ?, received_time = ?, is_read = 0 
                    WHERE id = ?
                    """,
                    (updated, current_time, row['id'])
                )
            else:
                # 创建新记录
                cursor.execute(
                    """
                    INSERT INTO chat_messages 
                    (friend_name, received_messages, is_read, received_time) 
                    VALUES (?, ?, 0, ?)
                    """,
                    (friend_name, message, current_time)
                )
            
            conn.commit()
    
    def get_unread_messages(self, friend_name: Optional[str] = None) -> List[Dict]:
        """获取未读消息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if friend_name:
                cursor.execute(
                    """
                    SELECT friend_name, received_messages, received_time 
                    FROM chat_messages 
                    WHERE friend_name = ? AND is_read = 0
                    """,
                    (friend_name,)
                )
            else:
                cursor.execute(
                    """
                    SELECT friend_name, received_messages, received_time 
                    FROM chat_messages 
                    WHERE is_read = 0
                    """
                )
            
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append({
                    "friend_name": row['friend_name'],
                    "received_messages": row['received_messages'],
                    "received_time": row['received_time']
                })
            
            return result
    
    def mark_as_read(self, friend_name: Optional[str] = None):
        """标记消息为已读"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if friend_name:
                cursor.execute(
                    "UPDATE chat_messages SET is_read = 1 WHERE friend_name = ? AND is_read = 0",
                    (friend_name,)
                )
            else:
                cursor.execute("UPDATE chat_messages SET is_read = 1 WHERE is_read = 0")
            
            conn.commit()
    
    def get_chat_history(self, friend_name: str, limit: int = 20) -> List[Dict]:
        """获取聊天历史记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT friend_name, received_messages, sent_messages, received_time, sent_time, is_read 
                FROM chat_messages 
                WHERE friend_name = ? 
                ORDER BY id DESC 
                LIMIT ?
                """,
                (friend_name, limit)
            )
            
            rows = cursor.fetchall()
            
            # 转换为字典列表
            result = []
            for row in rows:
                result.append({
                    "friend_name": row['friend_name'],
                    "received_messages": row['received_messages'],
                    "sent_messages": row['sent_messages'],
                    "received_time": row['received_time'],
                    "sent_time": row['sent_time'],
                    "is_read": row['is_read']
                })
            
            return result
    

