import os
import json
import requests
import pickle
import argparse
import time

amsterdam = [4.8896, 52.3576, 4.9186, 52.3776]
# Directory where images will be saved
save_dir = r"C:\svi\mapillary-api\data\1_retry"  # Replace with your desired directory path

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
    'code':'AQCCSZREkq8WQnHZ2mpt6a2jwou3u5ncBeivDWZ8gbrHAzf2sr8S4eV8yRsMIoZfH707xgSj8AR7SgyNYra56bvQzno5tRQ7F6Ezk40MjKpt2VPlD6SrtFpT-nKiN1MCPTCsTiyBRKJLonFoqXdC8ZlfX8BfpmbUvVK8brdMZg8M0Cob5OFrfK-jrwyDZ6pIkDZEnZAYvxlD5N1IZOXv4Uy8fHP979U0FTX4ak_AnDKg_TWJ0-SHx_IjhqQ6H_hfHzUOG3zC_ug26bURezsaAWkMKPf7rWiNujTZmXHmMKpKLw'
	#code--授权代码
}

r = requests.post(url=url,data=data,headers=headers)
response_data = json.loads(r.text)

# Extract the access token
access_token = response_data['access_token']


# Create the directory if it does not exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

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

# Read the JSON file
with open(r'C:\svi\mapillary-api\data\metadata\1_filtered.json', 'r') as f:
    data = json.load(f)

# Rectangle area coordinates
west, south, east, north = amsterdam

# Add a counter for failed requests
failed_requests = 0
max_retries = 3
retry_delay = 5  # seconds

# Iterate over all features
for feature in data['features']:
    # Get the coordinates of each feature
    lng = feature['geometry']['coordinates'][0]
    lat = feature['geometry']['coordinates'][1]
    
    # Check if the feature is within the rectangle area
    if west < lng < east and south < lat < north:
        # Get the image ID
        image_id = feature['properties']['id']
        
        # Skip if already processed
        if image_id in processed_ids:
            continue
        
        # Request the original image URL
        header = {'Authorization': 'OAuth {}'.format(access_token)}
        url = f'https://graph.mapillary.com/{image_id}?fields=thumb_original_url'
        
        for attempt in range(max_retries):
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
                    failed_requests = 0  # Reset failed requests counter on success
                else:
                    print(f'No image URL found for image ID {image_id}.')
                
                break  # Break the retry loop on success
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching image data for image ID {image_id}: {e}")
                failed_requests += 1
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Max retries reached for image ID {image_id}. Moving to next image.")
            
            # Check for consecutive failures and exit if too many
            if failed_requests >= 10:
                print("Too many consecutive failed requests. Exiting.")
                break
        
        # Update processed IDs and save checkpoint
        processed_ids.add(image_id)
        checkpoint = {
            'processed_ids': processed_ids,
            'image_count': image_count
        }
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint, f)

print(f'Download completed. Total images saved: {image_count}')
print(f'Total features processed: {len(processed_ids)}')