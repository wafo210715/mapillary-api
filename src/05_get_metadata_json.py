import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os

amsterdam = [-0.805, 50.800, -0.738, 50.897]


output_dir = r'C:\svi\mapillary-api\data\metadata'

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
    'code':'AQAwk80V-7Tm_qUgAZ-8PFA062ldNlC4RuyQzBRH-Rb-ewGTKQLTq7e0PYtRGISix1KINq_avGl4-lVB2jAGop4H1cs4UNFOCWFnuiLomAAtNYVQyWs0CdFOk10IdEUwHRWKHq3FEW5h_fJ2KACAYgHq44QmpEUtMj-U49j9OMuXkTXgNINMXDI_4Y4vAi5ZcLtvv50JFZylGkNQBeJO5JdhKUR870rbPIqBx5BhGdIIE_xgGW3bn-d4V-55yekmQCpazsnJjQcDR0q0UITamRAX5hKRx43DZRF8HK1HVBMztQ'
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']

west, south, east, north = amsterdam
tiles = list(mercantile.tiles(west, south, east, north, 14))

print(f"Number of tiles: {len(tiles)}")

num = 1
for tile in tiles:
    # Construct URL
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
            continue
        
        # Convert to JSON string
        json_data = json.dumps(data, indent=4)
        
        # Save the metadata
        output_path = os.path.join(output_dir, f'{num}.json')
        with open(output_path, 'w') as f:
            f.write(json_data)
        print(f'Successfully saved metadata json to {output_path}')
        
        num += 1
        
        # Break after processing one tile (for testing)
        break
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while requesting tile: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")

# ... rest of the code ...