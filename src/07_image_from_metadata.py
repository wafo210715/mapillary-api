import os
import json
import requests

amsterdam = [4.8896, 52.3576, 4.9186, 52.3776]
# Directory where images will be saved
save_dir = r"C:\svi\mapillary-api\data\1"  # Replace with your desired directory path

# https://www.mapillary.com/connect?client_id=26242695162043863

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
    'code':'AQCLW2SWG36E3qOkh-YWzxoFXG2femGbmCGyjgLbfrJ9rffboosuVd2skAWVGHZH3zvCB7GSup69sI_PGOkow8CjuQFlF1KJOX1kr40IFh_s9YBtML0GruE8GJ8T5f3itTu0gzSSdFQeZaL0AUpZGKtnIKijCg76W10g3IWVjdT7z85ldtmAYtKTDOn8PNcUfm9OzjtUQyhkAgFSfWFlXby0fNdufceJZFn2vnoIUED3_eVRJpfK9ZWsJ4GML98ig1yj94bPL_Xu9eI2mVW1FcqKbbNsyg0YVeT8mh4gRfNJPw'
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']


# Create the directory if it does not exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Read the JSON file
with open(r'C:\svi\mapillary-api\data\metadata\1.json', 'r') as f:
    data = json.load(f)

# Rectangle area coordinates
west, south, east, north = amsterdam


image_count = 0

# Iterate over all features
for feature in data['features']:
    # Get the coordinates of each feature
    lng = feature['geometry']['coordinates'][0]
    lat = feature['geometry']['coordinates'][1]
    
    # Check if the feature is within the rectangle area
    if west < lng < east and south < lat < north:
        # Get the image ID
        image_id = feature['properties']['id']
        
        # Request the original image URL
        header = {'Authorization': 'OAuth {}'.format(access_token)}
        url = f'https://graph.mapillary.com/{image_id}?fields=thumb_original_url'
        
        try:
            r = requests.get(url, headers=header)
            r.raise_for_status()
            image_data = r.json()
            
            # Get the image URL
            image_url = image_data.get('thumb_original_url')
            if image_url:
                # Save the image to the specified directory
                image_path = os.path.join(save_dir, f'{image_id}.jpg')
                with open(image_path, 'wb') as f:
                    image_content = requests.get(image_url, stream=True).content
                    f.write(image_content)
                print(f'Image {image_id}.jpg saved successfully in {save_dir}.')
                image_count += 1
            else:
                print(f'No image URL found for image ID {image_id}.')
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image data for image ID {image_id}: {e}")

print(f'Download completed. Total images saved: {image_count}')