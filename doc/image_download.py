import os
import json
import requests
import pickle
import argparse
import time
import math

# Directory where images will be saved
save_dir = r"C:\svi\data\amsterdam\1000m"  # Replace with your desired directory path

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
    'code':'AQAtk8rxp9-CV_ANHRvTtBiwEc9COIAuKQVKcmVL6O8SdSt6bgt994gkNBefgMiUf4MkzDHdNbAhh7s2wVhV7_c2TiAOFU1mdjq9l7xbX9YidRUV7vFUsRpqOgo9vNE1ZjDzH3GK2dPsgk_gDMW0pkaFB0Ws5ZgcgobS-dxIs3e3ShuMn1_SI_dURd5Xhb_MK_SufGZ7-i2Psh5hmBHMkwH-qF8aFSrNNIsc8CAoi59dEvRb9MesqH0s0ij_z_qBh-7Zv7loTxkJ3L-P05sCjxflbjjNYq58KlyYTWNKjXxFNw'
	#code--授权代码
}

r = requests.post(url=url, data=json.dumps(data), headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']


# Create the directory if it does not exist
os.makedirs(save_dir, exist_ok=True)

# Checkpoint file path
checkpoint_file = os.path.join(save_dir, 'checkpoint.pkl')

# Add command-line argument parsing
parser = argparse.ArgumentParser(description='Download images from Mapillary API')
parser.add_argument('--fresh-start', action='store_true', help='Start a fresh download, ignoring existing checkpoint')
args = parser.parse_args()

# Modify the checkpoint loading section
if os.path.exists(checkpoint_file) and not args.fresh_start:
    with open(checkpoint_file, 'rb') as f:
        checkpoint = pickle.load(f)
    processed_ids = checkpoint['processed_ids']
    image_count = checkpoint['image_count']
    print(f"Resuming from checkpoint. {image_count} images already processed.")
else:
    processed_ids = set()
    image_count = 0
    print("Starting a fresh download.")

# Read the JSON file for the 300m bounding box
with open(r"C:\svi\data\metadata\amsterdam\amsterdam_1000m.json", 'r') as f:
    data = json.load(f)

# Define the exact 300m bounding box coordinates
center_lat, center_lon = 52.3676, 4.9041  # Amsterdam center coordinates
side_length_m = 1000
lat_change = (side_length_m / 2) / 111111
lon_change = (side_length_m / 2) / (111111 * math.cos(math.radians(center_lat)))

bbox_300m = [
    center_lon - lon_change,  # west
    center_lat - lat_change,  # south
    center_lon + lon_change,  # east
    center_lat + lat_change   # north
]

# Modify the main loop
total_features = len(data['features'])
print(f"Total features in JSON: {total_features}")

for index, feature in enumerate(data['features'], 1):
    image_id = feature['properties']['id']
    
    # Check if the image is panoramic
    if feature['properties'].get('is_pano', False):
        print(f"Skipping panoramic image {image_id}.")
        continue
    
    # Check if the image is within the 300m bounding box
    if 'geometry' not in feature or 'coordinates' not in feature['geometry']:
        print(f"Skipping image {image_id} due to missing geometry information.")
        continue
    
    lon, lat = feature['geometry']['coordinates']
    if not (bbox_300m[0] <= lon <= bbox_300m[2] and bbox_300m[1] <= lat <= bbox_300m[3]):
        print(f"Skipping image {image_id} as it's outside the 300m bounding box.")
        continue
    
    if image_id in processed_ids:
        continue
    
    header = {'Authorization': f'OAuth {access_token}'}
    url = f'https://graph.mapillary.com/{image_id}?fields=thumb_original_url'
    
    max_retries = 3
    retry_delay = 5
    failed_requests = 0

    for attempt in range(max_retries):
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
                print(f'Image {image_id}.jpg saved successfully in {save_dir}. Progress: {index}/{total_features}')
                image_count += 1
                failed_requests = 0
            else:
                print(f'No image URL found for image ID {image_id}. Progress: {index}/{total_features}')
            
            break
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image data for image ID {image_id}: {e}")
            failed_requests += 1
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Max retries reached for image ID {image_id}. Moving to next image.")
        
        if failed_requests >= 10:
            print("Too many consecutive failed requests. Exiting.")
            break
    
    processed_ids.add(image_id)
    checkpoint = {
        'processed_ids': processed_ids,
        'image_count': image_count
    }
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(checkpoint, f)

    if index % 100 == 0:
        print(f"Processed {index}/{total_features} features. Images saved: {image_count}")

print(f'Download completed. Total images saved: {image_count}')
print(f'Total features processed: {len(processed_ids)}')