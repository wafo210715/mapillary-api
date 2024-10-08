import requests

code = ''

# get access token
url = 'https://graph.mapillary.com/token'
# 请求头
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'OAuth MLY|26242695162043863|b19a34f00f5d3ceb2cd7711600a1be8e'
    # Authorization--对应我们注册application的Client secret
}
# post请求发送的数据
data = {
    'grant_type': "authorization_code",
    'client_id': 26242695162043863,
    #client_id--对应我们注册application的Client ID - 这里就是授权代码
    'code':code
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
print(r.text)
# 保存成json文件，便于后期的复制
with open('token_info.json','w') as f:
    f.write(r.text)
print('done！')