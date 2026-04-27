# from openai import OpenAI

# client = OpenAI(
#     base_url="http://172.20.19.87:8642/v1",
#     api_key="2cf7f73cd69db3d3961d8ad1ccd976a33e5b35bd5e9d95e4404219a1b87127fa"
# )

# resp = client.chat.completions.create(
#     model="hermes",
#     messages=[
#         # {"role":"system", "content": ""},
#         {"role":"user", "content": "你直接用skill帮我回复消息啊!"}
#     ],
#     extra_headers={
#         "X-Hermes-Session-Id": "test_0"
#     }
# )
# print(resp.choices[0].message.content)



import requests

url = "http://172.20.19.87:8642/v1/responses"
api_key = "2cf7f73cd69db3d3961d8ad1ccd976a33e5b35bd5e9d95e4404219a1b87127fa"

data = {
    "model": "hermes-agent",
    "input": "她叫小美,网上认识的. 你直接输出回复她的内容, 不要输出无关的内容.   她发送的内容: 哈哈哈,睡觉了 ",
    "conversation": "test_00"
}
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
# resp = requests.post(url, json=data, headers=headers)
resp = requests.post(url, json=data, headers=headers)

print(resp.json())
resp_json = resp.json()
text = resp_json["output"][-1]["content"][0]["text"]
print(text)
import os
os.write



# import requests
# session = requests.Session()
# session.trust_env = False  # 关键：完全禁用系统代理
# url = "http://172.20.19.87:8642/v1/models"
# headers = {
#     "Authorization": "Bearer 2cf7f73cd69db3d3961d8ad1ccd976a33e5b35bd5e9d95e4404219a1b87127fa"
# }
# resp = session.get(url, headers=headers)
# print(resp.text)

