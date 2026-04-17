

# from pyweixin import Messages, Tools
# import sys
#
# try:
#     # 检查微信是否运行
#     if not Tools.is_weixin_running():
#         print("错误：微信未运行，请先打开并登录微信！")
#         sys.exit(1)
#
#
#     # 发送消息给马锋
#     Messages.send_messages_to_friend(
#         friend='马锋',
#         messages=['在不在？'],
#         close_weixin=False  # 不关闭微信窗口
#     )
#
#     print("✓ 消息已成功发送给马锋")
#
# except Exception as e:
#     print(f"✗ 发送失败：{e}")
#     print("\n请检查：")
#     print("1. 微信是否已打开并登录")
#     print("2. 通讯录中是否有备注为'马锋'的好友")
#     print("3. 是否已开启 Windows 讲述人（设置 -> 辅助功能 -> 讲述人）")
#     sys.exit(1)

#
# from pyweixin import Navigator
# from concurrent.futures import ThreadPoolExecutor
# from pyweixin import Navigator,AutoReply
# #自动回复函数传入参数是字符串和字符串列表(消息列表内所有可见的文本,可作为上下文),返回值须为字符串类型
# def reply_func1(newMessage:str,contexts:list[str]):
#     if '你好' in newMessage:
#         return '.'
#     if '在吗' in newMessage:
#         return '..'
#     return '...'
#
# def reply_func2(newMessage:str,contexts:list[str]):
#     return '........'
#
# #先打开所有好友的独立窗口
# dialog_windows=[]
# friends=['马锋','黎佳霖']
# for friend in friends:
#     dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
#     dialog_windows.append(dialog_window)
# durations=['1min','1min']
# callbacks=[reply_func1,reply_func2]
# with ThreadPoolExecutor() as pool:
#     results=pool.map(lambda args: AutoReply.auto_reply_to_friend(*args),list(zip(dialog_windows,durations,callbacks)))
# for friend,result in zip(friends,results):
#     print(friend,result)




### 多线程打开多个好友窗口进行消息监听
# from concurrent.futures import ThreadPoolExecutor
# from pyweixin import Navigator,Monitor
# #先打开所有好友的独立窗口
# dialog_windows=[]
# friends=['马锋','黎佳霖']
# durations=['1min']*len(friends)
# #不添加其他参数Monitor.listen_on_chat,比如save_photos,该操作涉及键鼠,无法多线程，只是监听消息，获取文本内容,移动保存文件还是可以的
# for friend in friends:
#     dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)#window_minimize独立窗口最小化
#     dialog_windows.append(dialog_window)
# with ThreadPoolExecutor(max_workers=len(friends)) as pool:
#     results=pool.map(lambda args: Monitor.listen_on_chat(*args),list(zip(dialog_windows,durations)))
# for friend,result in zip(friends,results):
#     print(friend,result)




# ### 获取'马锋'的聊天记录代码
# from pyweixin import Messages

# # 获取马锋的最近10条聊天记录
# messages, timestamps = Messages.dump_chat_history(
#     friend='马锋',
#     number=10,  # 获取10条消息
#     search_pages=5,  # 在会话列表中查找好友时滚动的次数
#     is_maximize=False,  # 微信界面不全屏
#     close_weixin=False  # 不关闭微信
# )

# # 打印聊天记录
# print(f"\n=== 与马锋的聊天记录（共{len(messages)}条）===\n")
# for i, (message, timestamp) in enumerate(zip(messages, timestamps), 1):
#     print(f"[{i}] 时间: {timestamp}")
#     print(f"    内容: {message}")
#     print("-" * 50)



# ### 获取'马锋'的所有聊天记录
# from pyweixin import Messages

# # 获取所有聊天记录
# messages, timestamps = Messages.dump_chat_history(
#     friend='马锋',
#     number=99999,  # 设置很大的数字，自动获取所有记录
#     close_weixin=False
# )

# # 打印所有聊天记录
# print(f"\n共获取 {len(messages)} 条聊天记录：\n")
# for i, message in enumerate(messages, 1):
#     print(f"{i}. {message}\n")


### 一直（死循环）监听多个好友（'马锋','黎佳霖'）的消息，也包括自己的，监听到消息后立刻输出到控制台
from pyweixin import Navigator, Tools
from pyweixin.Uielements import Lists, Buttons
import time

# 实例化
Lists = Lists()
Buttons = Buttons()

# 监听的好友列表
friends = ['马锋', '黎佳霖']

# 打开所有好友的独立窗口并获取自己的名字
dialog_windows = []
my_name = None

for friend in friends:
    dialog_window = Navigator.open_seperate_dialog_window(
        friend=friend, 
        window_minimize=True, 
        close_weixin=True
    )
    dialog_windows.append(dialog_window)
    
    # 获取自己的名字（只需要获取一次）
    if my_name is None:
        try:
            # 尝试从主窗口获取自己的名字
            main_window = Navigator.open_weixin(is_maximize=False)
            my_button = main_window.child_window(**Buttons.MySelfButton)
            if my_button.exists():
                my_name = my_button.window_text()
            main_window.close()
        except:
            my_name = "我"  # 默认值

print(f"监听已启动，我的名字: {my_name}")

# 记录每个窗口的最后一条消息ID
last_message_ids = {}
for window in dialog_windows:
    chatList = window.child_window(**Lists.FriendChatList)
    if chatList.children(control_type='ListItem'):
        last_message_ids[window] = chatList.children(control_type='ListItem')[-1].element_info.runtime_id
    else:
        last_message_ids[window] = 0

# 死循环监听
while True:
    for friend, window in zip(friends, dialog_windows):
        chatList = window.child_window(**Lists.FriendChatList)
        if chatList.children(control_type='ListItem'):
            newMessage = chatList.children(control_type='ListItem')[-1]
            runtime_id = newMessage.element_info.runtime_id
            
            if runtime_id != last_message_ids[window]:
                content = newMessage.window_text()
                
                # 通过is_my_bubble判断是否是自己发的
                is_mine = Tools.is_my_bubble(window, newMessage)
                sender = my_name if is_mine else friend
                
                print(f"[{friend}] {sender}: {content}")
                
                last_message_ids[window] = runtime_id
    
    time.sleep(1)  # 每秒检查一次

