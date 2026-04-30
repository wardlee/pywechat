你先分析，并告诉最少代码解决问题的方法有哪些，列出来，我选择后再写代码。

你先分析，并列出解决这个问题的方案有哪些， 方案要简洁，至少出列出2个方案，我选择后再写代码。







# 需求

## 增加获取历史记录的API，参数：好友名称，聊天记录条数=20
这个消息是直接给人看的，所以返回格式如下:
正常返如下：
``` txt
当前时间： 26年04月27日 17:30

[25年12月03日 17:13][小花]： 具体消息内容
[01月03日 12:13][我]： 具体消息内容
[04月27日 09:10][小花]： 具体消息内容
[04月27日 11:10][我]： 具体消息内容
[04月27日 11:10][未读,待回复][小花]： 具体消息内容
```
有异常时返回如下：
``` txt
没有记录
```








# 修改
"OpenAI": {
    "url": "https://api-inference.modelscope.cn/v1",
    "key": "ms-c7341323-641d-4a13-ae90-6f6438f35eb8",
    "model_name": "moonshotai/Kimi-K2.5"
},
"FallBack": {
    "url": "",
    "key": "",
    "model_name": ""
}

需要改成：

[
    "A Provider": {
        "A Provider": {
            "url": "https://api-inference.modelscope.cn/v1",
            "key": "ms-c7341323-641d-4a13-ae90-6f6438f35eb8",
            "model_name": ["moonshotai/Kimi-K2.5","moonshotai/Kimi-K2.6"]
        }
    }
    "B Provider": {
        "A Provider": {
            "url": "https://api-inference.modelscope.cn/v1",
            "key": "ms-c7341323-641d-4a13-ae90-6f6438f35eb8",
            "model_name": ["moonshotai/Kimi-K2.7","moonshotai/Kimi-K2.8"]
        }
    }
]

切换逻辑：
轮流切换模型，从第一个模型开始，依次切换到下一个模型，直到最后一个模型。
比如K2.5重试后不行再切K2.6，再不行再切K2.7，再不行再切K2.8。
切完一轮才抛异常，比如从K2.6开始切换，切了一轮，切到K2.5，再切到2.6还是不行，才报异常。
如果是网络超时等原因，可以重试，如果模型被限制等直接快速跳过下一个模型