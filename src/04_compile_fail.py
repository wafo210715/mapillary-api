import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os
import sys

code='AQC94UtZaHYLqAcKgAlCqOdqJyotU9PKBSJ2Y8SH8KNgjw9ZbJG88hc2y5Ij0PMiyQOfl2NTJE9w-sruOZpLKJ-zn0rFZa6bVr-9vedHapYIK5z44A5FDDpT7iGxxlSNa4t8YMWl5SSWNoz1YnGM3ot6lgOYH0IoOvEgpYeFnPy8JVMkdj6_OX31aMOt97eLO-MdWav7TVk9IStR1WeXyj20TtUvqRgcwHHITlWeDIqTPOq8--oSxajg3ITHACiuQe1UbiKnUYrn4U_kXv6uwF9gXjaVRQD0Pp3NYt28fO2F_g'

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
# Parse the JSON response
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']






amsterdam = [4.88965, 52.37403, 5.01699, 52.39362]
west, south, east, north = amsterdam
tiles = list(mercantile.tiles(west, south, east, north, 14))
print(f"Number of tiles: {len(tiles)}")

access_token = 'MLYARBZBxZCqAt76zO5tdIjaO5cnsssCLadLxleWv7bfBXQq8dnPrMvTT6rN4L6kHcZBaIK2JLL3ef6b3yyBWILOyVqCN1ZCR4ovGZCHT4mmGsleIfhkNpv2DZBnZCAjsg0QZDZD' 

num = 1
# 这里的变量tiles是第一部分中得到的
for tile in tiles:
	# 构造url
	tile_url = 'https://tiles.mapillary.com/maps/vtp/mly1_public/2/{}/{}/{}?access_token={}'.format(tile.z,tile.x,tile.y,access_token)
	# 发GET请求
	try:
		response = requests.get(tile_url)
		response.raise_for_status()  # This will raise an exception for HTTP errors
		print(f"Tile request successful. Status code: {response.status_code}")
		
		data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer="image")
		if not data['features']:
			print(f"Warning: No features found in tile {tile}")
			continue
		
		data = json.dumps(data, indent=4)
		
		# Use an absolute path for saving the file
		file_path = os.path.join(os.getcwd(), f'{num}.json')
		with open(file_path, 'w') as f:
			f.write(data)
		print(f'Successfully saved data to {file_path}')
		num = num + 1
		
		# Break after processing one tile (for testing)
		break
	
	except requests.exceptions.RequestException as e:
		print(f"Error occurred while requesting tile: {e}")
	except Exception as e:
		print(f"Unexpected error occurred: {e}")
		print(f"Error type: {type(e).__name__}")
		print(f"Error details: {str(e)}")

# Directory where images will be saved
save_dir = r'C:\svi\mapillary-api\data\demo test'  # Replace with your desired directory path

# Create the directory if it does not exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Read the JSON file
with open('1.json', 'r') as f:
    data = json.load(f)


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