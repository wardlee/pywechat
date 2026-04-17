# PyWeixin 🥇
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/wechat.png)

## 🍬🍬 微信 RPA 工具，支持微信 4.1+ 版本

详细使用方法见：https://github.com/Hello-Mr-Crab/pywechat/blob/main/Weixin4.0.md

### PyWeixin 是一个基于 pywinauto 实现的 Windows 系统下 PC 微信自动化（pure UI automation）的 Python 项目（不涉及逆向 Hook 操作），实现了 PC 微信内置的大部分功能。

### 微信版本：4.1+
### 操作系统：🪟 Windows 7 / 🪟 Windows 10 / 🪟 Windows 11
### Python 版本🐍：3.9+（支持 TypeHint）
### 支持语言：简体中文、English、繁体中文

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/pyweixin结构.png)
<br>

## pyweixin 内所有方法需要先导入模块下的类然后调用内部方法🗺️🗺️
```python
from pyweixin import xx(class)
xx(class).yy(method)
```
<br>

### 获取方法：
```bash
git clone https://github.com/Hello-Mr-Crab/pywechat.git
```
<br>

### pyweixin 模块介绍
#### WechatTools🌪️🌪️
##### class包括:
- `Tools`:关于PC微信的一些工具,微信路径,运行状态,以及内部一些UI相关的判别方法。
- `Navigator`:打开微信内部一切可以打开的界面。
<br>

#### WechatAuto🛏️🛏️
##### class包括：
- `AutoReply`:自动回复操作
- `Call`: 给某个好友打视频或语音电话。
- `Contacts`: 获取通讯录内各分区(联系人,企业微信联系人,公众号,服务号)好友的信息,获取共同群聊名称,获取好友个人简介
- `Files`: 文件发送，聊天文件从本地导出等。
- `FriendSettings`: PC微信针对某个好友的一些相关设置。
- `Messages`: 消息发送,聊天记录获取,聊天会话导出等条。
- `Moments`:针对微信朋友圈的一些方法,包括朋友圈界面内容获取，发布朋友圈
- `Monitor`:打开聊天窗口进行监听消息
<br>

#### WinSettings🔹🔹
##### class包括：
- `SystemSettings`:该模块中提供了一些修改windows系统设置的方法(在自动化过程中)。
<br>

#### utils🍬🍬
##### 内部的一些函数主要用来二次开发,大部分传入的参数是main_window,pywinauto实例化的对象(使用Navigator.open_weixin打开)
##### class包括：
- `Regex_Patterns`:自动化过程中用到的正则pattern。
##### func包括:
- `At`:在群聊中At指定的一些好友
- `At_all`:在群聊中At所有人
- `auto_reply_to_friend_decorator`:自动回复好友装饰器
- `get_new_message_num`：获取新消息总数,微信按钮上的红色数字
- `scan_for_newMessages`：会话列表遍历一遍有新消息提示的对象,返回好友名称与数量
- `open_red_packet`: 点击打开好友发送的红包
- `language_detector`:微信当前使用语言检测(不能禁用WeChatAppex.exe(涉及到公众号,微信内置浏览器,视频号等功能),原理是查询WeChatAppex.exe命令行参数)
<br>

### pyweixin 使用示例：
#### 所有自动化操作只需两行代码即可实现，即：
```python
from pyweixin import xxx
xxx.yy
```
<br>


#### 多线程监听消息
```python
# 多线程打开多个好友窗口进行消息监听
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator, Monitor

# 先打开所有好友的独立窗口
dialog_windows = []
friends = ['Hello,Mr Crab', 'Pywechat测试群']
durations = ['1min'] * len(friends)

# 不添加其他参数 Monitor.listen_on_chat，比如 save_photos，该操作涉及键鼠，无法多线程
# 只是监听消息，获取文本内容，移动保存文件还是可以的
for friend in friends:
    dialog_window = Navigator.open_seperate_dialog_window(
        friend=friend, 
        window_minimize=True, 
        close_weixin=True
    )  # window_minimize 独立窗口最小化
    dialog_windows.append(dialog_window)

with ThreadPoolExecutor(max_workers=len(friends)) as pool:
    results = pool.map(
        lambda args: Monitor.listen_on_chat(*args), 
        list(zip(dialog_windows, durations))
    )

for friend, result in zip(friends, results):
    print(friend, result)
```
<br>

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/listen_on_chat多线程.png)

<br>

#### 多线程监听消息并自动回复
```python
from pyweixin import Navigator
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator, AutoReply

# 自动回复函数传入参数是字符串和字符串列表（消息列表内所有可见的文本，可作为上下文）
# 返回值须为字符串类型
def reply_func1(newMessage: str, contexts: list[str]):
    if '你好' in newMessage:
        return '你好，有什么可以帮您的吗[呲牙]?'
    if '在吗' in newMessage:
        return '在的[旺柴]'
    return '自动回复[微信机器人]：您好，我当前不在，请您稍后再试'

def reply_func2(newMessage: str, contexts: list[str]):
    return '自动回复[微信机器人]：您好，我当前不在，请您稍后再试'

# 先打开所有好友的独立窗口
dialog_windows = []
friends = ['abcdefghijklmnopqrstuvwxyz123456', 'Pywechat测试群']
for friend in friends:
    dialog_window = Navigator.open_seperate_dialog_window(
        friend=friend, 
        window_minimize=True, 
        close_weixin=True
    )
    dialog_windows.append(dialog_window)

durations = ['1min', '1min']
callbacks = [reply_func1, reply_func2]

with ThreadPoolExecutor() as pool:
    results = pool.map(
        lambda args: AutoReply.auto_reply_to_friend(*args), 
        list(zip(dialog_windows, durations, callbacks))
    )

for friend, result in zip(friends, results):
    print(friend, result)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/自动回复.png)

<br>

#### 监听单个聊天窗口消息
```python
from pyweixin import Navigator, Monitor

dialog_window = Navigator.open_seperate_dialog_window(friend='啦啦啦')
result = Monitor.listen_on_chat(dialog_window=dialog_window, duration='30s')
print(result)  # 返回值 {'新消息总数': x, '文本数量': x, '文件数量': x, '图片数量': x, '视频数量': x, '链接数量': x, '文本内容': x}
```

<br>

#### 朋友圈数据获取
```python
from pyweixin import Moments

posts = Moments.dump_recent_posts(recent='Today')
for dic in posts:
    print(dic)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/朋友圈数据获取.png)

<br>

#### 发布朋友圈
```python
from pyweixin import Moments

Moments.post_moments(
    texts='''发布朋友圈测试[旺柴]''', 
    medias=[r"E:\Desktop\test0.png", r"E:\Desktop\test1.png"]
)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/发朋友圈.png)

<br>

#### 好友朋友圈内容导出
```python
from pyweixin import Moments

Moments.dump_friend_posts(
    friend='xxx', 
    number=3, 
    save_detail=True, 
    target_folder=r"E:\Desktop\好友朋友圈内容导出"
)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/好友朋友圈内容导出.png)
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/好友朋友圈内容.png)

<br>

#### 好友朋友圈自定义评论
```python
from pyweixin import Moments

def comment_func(content):
    if 'xxx' in content:
        return 'yyy'
    return 'zzz'

Moments.like_friend_posts(
    friend='xxx', 
    number=20, 
    callback=comment_func, 
    use_green_send=True
)
```

<br>

#### 此外 pyweixin 内所有方法及函数的一些位置参数支持全局设定，be like：
```python
from pyweixin import Navigator, GlobalConfig

GlobalConfig.load_delay = 2.5
GlobalConfig.is_maximize = True
GlobalConfig.close_weixin = False

Navigator.search_channels(search_content='微信4.0')
Navigator.search_miniprogram(name='问卷星')
Navigator.search_official_account(name='微信')
```
<br>

#### 公众号文章 URL 获取
```python
from pyweixin import Collections

Collections.collect_offAcc_articles(name='新华社', number=10)
urls = Collections.cardLink_to_url(number=10)
for url, text in urls.items():
    print(f'{text}\n{url}')
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/公众号文章url获取.png)

<br>

#### 其他类内 method 使用方法可见代码中详细的文档注释以及 pyweixin操作手册.docx
<br>
## 注意：
👎👎 请勿将 pyweixin 用于任何非法商业活动，因此造成的一切后果由使用者自行承担！

##### 本项目相关博客
- `pywinauto使用教程`:https://mrcrab.blog.csdn.net/article/details/157546162?fromshare=blogdetail&sharetype=blogdetail&sharerId=157546162&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `python正则表达式`:https://mrcrab.blog.csdn.net/article/details/151123336?fromshare=blogdetail&sharetype=blogdetail&sharerId=151123336&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `shutil文件移动`:https://mrcrab.blog.csdn.net/article/details/148735930?fromshare=blogdetail&sharetype=blogdetail&sharerId=148735930&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `os.path文件路径`:https://mrcrab.blog.csdn.net/article/details/147304200?fromshare=blogdetail&sharetype=blogdetail&sharerId=147304200&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `x86虚拟机安装问题`:https://mrcrab.blog.csdn.net/article/details/158418985?fromshare=blogdetail&sharetype=blogdetail&sharerId=158418985&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link 
<br>

###### 作者CSDN主页:https://blog.csdn.net/weixin_73953650?spm=1011.2415.3001.5343
