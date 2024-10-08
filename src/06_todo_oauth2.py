import requests
import json
import mercantile
from vt2geojson.tools import vt_bytes_to_geojson
import os
import urllib.parse
import time

amsterdam = [4.8896, 52.3576, 4.9186, 52.3776]


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

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

def get_auth_code():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, AuthHandler)
    httpd.handle_request()
    return httpd.auth_code

# Usage
auth_code = get_auth_code()
print(f"Received authorization code: {auth_code}")

# Usage
client_id = 26242695162043863  # Your client ID
redirect_uri = "http://localhost:8080/callback"  # Your redirect URI
auth_url = get_auth_url(client_id, redirect_uri)
print(f"Please visit this URL to authorize the application: {auth_url}")

import requests

def exchange_code_for_token(client_id, client_secret, auth_code, redirect_uri):
    url = 'https://graph.mapillary.com/token'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'OAuth {client_secret}'
    }
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': auth_code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Usage
client_secret = 'your_client_secret'  # Replace with your actual client secret
token_data = exchange_code_for_token(client_id, client_secret, auth_code, redirect_uri)
access_token = token_data['access_token']
expires_in = token_data['expires_in']
print(f"Received access token: {access_token}")
print(f"Token expires in {expires_in} seconds")

# Store the token data
token_data = {
    'access_token': access_token,
    'expires_at': time.time() + expires_in
}

def get_valid_token():
    global token_data
    if time.time() >= token_data['expires_at'] - 300:  # Refresh if within 5 minutes of expiration
        new_token_data = refresh_token(client_id, client_secret, token_data['access_token'])
        token_data = {
            'access_token': new_token_data['access_token'],
            'expires_at': time.time() + new_token_data['expires_in']
        }
    return token_data['access_token']

# Usage in your main code
valid_token = get_valid_token()
# Use valid_token for your API requests