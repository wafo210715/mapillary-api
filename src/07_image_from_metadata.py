import os
import json
import requests
import pickle

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
    'code':'AQDI6YrtiOW5N5bLy_-deJcjpNtSXjXWKlPhsU_Eg7oPhNAYTrqNS3ROx4W-A7mKU3NLX-15ezwx931115vgACuE6DNFzkYGYm6hgxsL8NHYHfcxX-6RgTba3SOH54_dA9-reM-kg_stiC1N2w1JqqqoEvWF1N-IVqwoXnTFk5Y2kPVaNpQIN6oMzEFy-hUV1JMMKgvxDdOuU70QjRGDQP7Nj_M-Pq0bu6GzloN4FJr5rukhrjlS5AI47BZ_Isble_0zd6lmIyXxKYY71WzkUSeZtcZDF5oQrZ9_8odb2rb3Ow'
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

# Load checkpoint if it exists
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'rb') as f:
        checkpoint = pickle.load(f)
    processed_ids = checkpoint['processed_ids']
    image_count = checkpoint['image_count']
    print(f"Resuming from checkpoint. {image_count} images already processed.")
else:
    processed_ids = set()
    image_count = 0

# Read the JSON file
with open(r'C:\svi\mapillary-api\data\metadata\1_filtered.json', 'r') as f:
    data = json.load(f)

# Rectangle area coordinates
# this is the bounding box of amsterdam
# visualize it using 12_visualize_boundingbox.py
west, south, east, north = amsterdam


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

        # Update processed IDs and save checkpoint
        processed_ids.add(image_id)
        checkpoint = {
            'processed_ids': processed_ids,
            'image_count': image_count
        }
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint, f)

print(f'Download completed. Total images saved: {image_count}')