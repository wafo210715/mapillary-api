import requests
import mercantile
import folium
import json
from vt2geojson.tools import vt_bytes_to_geojson
import os

code = ''

chichester = [4.8896, 52.3576, 4.9186, 52.3776]
chichester_location = [4.8896, 52.3576]
amsterdam = [-0.805, 50.800, -0.738, 50.897]
amsterdam_location = [-0.805, 50.800]

city = amsterdam
city_location = amsterdam_location

zoom = 16
html_zoom = 9


def get_access_token(code):
    url = 'https://graph.mapillary.com/token'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth MLY|26242695162043863|b19a34f00f5d3ceb2cd7711600a1be8e'
    }
    data = {
        'grant_type': "authorization_code",
        'client_id': 26242695162043863,
        'code': code
    }
    r = requests.post(url=url, data=data, headers=headers)
    response_data = json.loads(r.text)
    access_token = response_data['access_token']
    return access_token



def get_tiles(west, south, east, north, zoom):
    m = folium.Map(location=city_location, zoom_start=html_zoom)
    tiles = list(mercantile.tiles(west, south, east, north, zoom))
    
    for tile in tiles:
        bounds = mercantile.bounds(tile)
        folium.Rectangle(
            bounds=[(bounds.south, bounds.west), (bounds.north, bounds.east)],
            color="red", weight=1
        ).add_to(m)
    m.save("amsterdam_tiles_" + str(zoom) + ".html")
    
    return tiles


def get_tile_metadata(tiles, access_token):
    for num, tile in enumerate(tiles, start=1):
        tile_url = f'https://tiles.mapillary.com/maps/vtp/mly1_public/2/{tile.z}/{tile.x}/{tile.y}?access_token={access_token}'
        response = requests.get(tile_url)
        data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z, layer="image")
        data = json.dumps(data, indent=4)
        
        with open(f'{num}.json', 'w') as f:
            f.write(data)
        print(f'Tile {num} metadata saved successfully!')

def create_save_directory(save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return save_dir

def download_images(json_file, save_dir, access_token, city):
    west, south, east, north = city
    image_count = 0

    with open(json_file, 'r') as f:
        data = json.load(f)

    for feature in data['features']:
        lng, lat = feature['geometry']['coordinates']
        
        if west < lng < east and south < lat < north:
            image_id = feature['properties']['id']
            header = {'Authorization': f'OAuth {access_token}'}
            url = f'https://graph.mapillary.com/{image_id}?fields=thumb_original_url'
            
            try:
                r = requests.get(url, headers=header)
                r.raise_for_status()
                image_data = r.json()
                
                image_url = image_data.get('thumb_original_url')
                if image_url:
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
    return image_count

def main():
    # Assuming these variables are defined earlier in the script
    access_token = get_access_token(code)
    west, south, east, north = city
    tiles = get_tiles(west, south, east, north, zoom)
    
    get_tile_metadata(tiles, access_token)
    
    save_dir = create_save_directory(os.path.join(r"C:\svi\mapillary-api\data", f"svi_{city}"))
    
    download_images('1.json', save_dir, access_token, city)

if __name__ == "__main__":
    main()
