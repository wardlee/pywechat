"""
测试数据库记录的详细信息
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
import time

def test_database_records():
    """测试数据库记录的详细信息"""
    
    # 使用测试数据库
    db = Database("test_records.db")
    
    print("=" * 60)
    print("测试: 数据库记录详细信息")
    print("=" * 60)
    
    friend_name = "李四"
    
    # 1. 保存第一条发送消息
    print("\n步骤1: 保存第一条发送消息")
    db.save_sent_message(friend_name, ["第一条消息"])
    time.sleep(1)
    
    # 2. 保存接收消息
    print("步骤2: 保存接收消息")
    db.save_received_message(friend_name, "收到了")
    time.sleep(1)
    
    # 3. 保存第二条发送消息（会合并到同一条记录）
    print("步骤3: 保存第二条发送消息")
    db.save_sent_message(friend_name, ["第二条消息"])
    
    # 4. 查看数据库原始记录
    print("\n" + "=" * 60)
    print("数据库原始记录:")
    print("=" * 60)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, friend_name, sent_messages, sent_time, 
                   received_messages, received_time, is_read
            FROM chat_messages 
            WHERE friend_name = ?
            ORDER BY id
        """, (friend_name,))
        
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            print(f"  ID: {row['id']}")
            print(f"  好友: {row['friend_name']}")
            print(f"  发送消息: {row['sent_messages']}")
            print(f"  发送时间: {row['sent_time']}")
            print(f"  接收消息: {row['received_messages']}")
            print(f"  接收时间: {row['received_time']}")
            print(f"  已读状态: {row['is_read']}")
    
    # 5. 标记为已读后再发送消息
    print("\n" + "=" * 60)
    print("步骤4: 标记为已读")
    print("=" * 60)
    db.mark_as_read(friend_name)
    
    time.sleep(1)
    
    print("步骤5: 标记已读后发送新消息")
    db.save_sent_message(friend_name, ["已读后的新消息"])
    
    # 6. 再次查看数据库记录
    print("\n" + "=" * 60)
    print("标记已读后的数据库记录:")
    print("=" * 60)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, friend_name, sent_messages, sent_time, 
                   received_messages, received_time, is_read
            FROM chat_messages 
            WHERE friend_name = ?
            ORDER BY id
        """, (friend_name,))
        
        rows = cursor.fetchall()
        
        for i, row in enumerate(rows, 1):
            print(f"\n记录 {i}:")
            print(f"  ID: {row['id']}")
            print(f"  好友: {row['friend_name']}")
            print(f"  发送消息: {row['sent_messages']}")
            print(f"  发送时间: {row['sent_time']}")
            print(f"  接收消息: {row['received_messages']}")
            print(f"  接收时间: {row['received_time']}")
            print(f"  已读状态: {row['is_read']}")
    
    # 7. 验证结果
    print("\n" + "=" * 60)
    print("验证结果:")
    print("=" * 60)
    
    history = db.get_chat_history(friend_name, limit=10)
    
    all_have_sent_time = True
    for record in history:
        if record['sent_messages'] and not record['sent_time']:
            all_have_sent_time = False
            print(f"✗ 发现没有发送时间的记录: {record}")
    
    if all_have_sent_time:
        print("✓ 所有包含发送消息的记录都有发送时间")
    
    # 验证接收时间
    all_have_received_time = True
    for record in history:
        if record['received_messages'] and not record['received_time']:
            all_have_received_time = False
            print(f"✗ 发现没有接收时间的记录: {record}")
    
    if all_have_received_time:
        print("✓ 所有包含接收消息的记录都有接收时间")
    
    print(f"\n总记录数: {len(history)}")
    
    # 清理测试数据库
    import os
    if os.path.exists("test_records.db"):
        os.remove("test_records.db")
        print("\n✓ 已清理测试数据库")


if __name__ == "__main__":
    try:
        test_database_records()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
