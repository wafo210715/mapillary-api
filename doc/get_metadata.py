import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os
from math import cos, radians

bbox_sizes = [300, 1000, 3000, 10000]  # Add this at the top of your script

output_dir = r'C:\svi\mapillary-api\data\metadata\amsterdam'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# https://www.mapillary.com/connect?client_id=26242695162043863


# Function to create a square bounding box
def create_square_bbox(center_lat, center_lon, side_length_m):
    lat_change = (side_length_m / 2) / 111111
    lon_change = (side_length_m / 2) / (111111 * cos(radians(center_lat)))
    
    return [
        center_lon - lon_change,  # west
        center_lat - lat_change,  # south
        center_lon + lon_change,  # east
        center_lat + lat_change   # north
    ]

# Amsterdam center coordinates
amsterdam_center = (52.3676, 4.9041)

# Create bounding boxes
bounding_boxes = [
    create_square_bbox(amsterdam_center[0], amsterdam_center[1], 300),
    create_square_bbox(amsterdam_center[0], amsterdam_center[1], 1000),
    create_square_bbox(amsterdam_center[0], amsterdam_center[1], 3000),
    create_square_bbox(amsterdam_center[0], amsterdam_center[1], 10000)
]


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
    'code':'AQC4fTBECg3dJxpKpKmx82MisE887jV258_CJeppP5DslUWfnV7g5wiWqeIpT0QRgW7Y39F1sGt8n249j_mkto91sziScQ2MC1sGjk0Ttc7zJASC6NjERvzHylLfdvE3NidTWfSTtJ9NZb71Mi-HQ8hUZgPTGeNEWyMInDdDumXr05zqGHL7MhtAweF9d44Lhus7tTjO-bS26eoHZf1hP8J5LbjX6VM3sjrcPMHOhy0PHCUrjpCmfWkO8OBmAUqp3rf3tjOVH1M9wxQnT6naFaPPBCGHbVNhRvTk5_x6q3pj6g'
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']

for i, (bbox, size) in enumerate(zip(bounding_boxes, bbox_sizes), 1):
    west, south, east, north = bbox
    tiles = list(mercantile.tiles(west, south, east, north, 14))

    print(f"Processing bounding box {i} ({west}, {south}, {east}, {north})")
    print(f"Number of tiles: {len(tiles)}")

    # Initialize an empty list to store all features
    all_features = []

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
            
            # Instead of saving each tile separately, append its features to all_features
            all_features.extend(data['features'])
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while requesting tile: {e}")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")

    # After processing all tiles for this bounding box, create a single GeoJSON object
    combined_geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }

    # Convert to JSON string
    json_data = json.dumps(combined_geojson, indent=4)

    # Save the combined metadata for this bounding box
    output_path = os.path.join(output_dir, f'amsterdam_{size}m.json')
    with open(output_path, 'w') as f:
        f.write(json_data)
    print(f'Successfully saved combined metadata json to {output_path}')

print("Finished processing all bounding boxes")