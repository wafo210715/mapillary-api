import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os

code = 'AQCTh8klj3gZQ93ymeshau0gMCvhmoD06MN97-9Cw8sqSTAkvU_alEV4jAyL80G8_-3p0DFS-D927A2_ZUq79VNLLHJauKzfoesF5mzEuHx6wWdSIcZYr1riB8YS5mf9cOkgUKNXtNDavVk885oFlCKXhDboIrAfaG0gNcqSdespaxHW2_ZJQjH8PPrUxKbrsNln0gM3ZMZyAeVosg3wq3Rajnxs0WDQZH44a0VycAAjJRRYPoD5_Jgak2U22-PdX2K8BmwgIwNmDu7nGbQQXOdRGPmATUy7Xg7JnhwDmON9Cw'

# get access token
url = 'https://graph.mapillary.com/token'
# headers request
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

# Parse the JSON response
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']


