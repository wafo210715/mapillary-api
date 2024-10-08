import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os

amsterdam = [4.8896, 52.3576, 4.9186, 52.3776]


output_dir = r'C:\svi\mapillary-api\data\metadata'
demotest_dir = os.path.join(output_dir, 'demotest')

# Create the demotest directory if it doesn't exist
os.makedirs(demotest_dir, exist_ok=True)

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
    'code':'AQBrZJuREdzZeqDZBvXsoC7It1t7MJWeOLm109emQ0wjK5JMXxGSykG7bB-al4VmTJ7cSjpw91RnC-Op2rWvBaWWZwF5lZWL_cnpEkOTqi_5C96BzfB5hEq9PPEmOSQC9LwfanbuXRanY_66coJuT3rEExXPxXF7pkAPabtGSSkBqYDILeu6G0NL8csT7ZxNcEAJYmhdup5j_GsNDo4d4ASFsffiqKL1e6N39YFM_VHfpCMK5ixUhHnGIKULkya5ow0H4KdRSgTo1VyhDjh-zi8zwuQQKdQ8bxLXYG4_rkthjA'
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']

west, south, east, north = amsterdam
tiles = list(mercantile.tiles(west, south, east, north, 14))

print(f"Number of tiles: {len(tiles)}")

# Select only the first tile
tile = tiles[0]

# Construct URL for the single tile
tile_url = f'https://tiles.mapillary.com/maps/vtp/mly1_public/2/{tile.z}/{tile.x}/{tile.y}?access_token={access_token}'
print(f"Requesting tile: {tile_url}")

try:
    # Send GET request
    response = requests.get(tile_url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    print(f"Tile request successful. Status code: {response.status_code}")
    
    # Convert vector tile to GeoJSON
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer="image")
    
    if not data['features']:
        print(f"Warning: No features found in tile {tile}")
    else:
        # Convert to JSON string
        json_data = json.dumps(data, indent=4)
        
        # Save the metadata
        output_path = os.path.join(demotest_dir, 'demo_tile.json')
        with open(output_path, 'w') as f:
            f.write(json_data)
        print(f'Successfully saved metadata json to {output_path}')

except requests.exceptions.RequestException as e:
    print(f"Error occurred while requesting tile: {e}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {str(e)}")

# ... rest of the code ...

