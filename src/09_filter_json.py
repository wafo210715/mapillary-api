import json

# Load the JSON data
with open('C:\\svi\\mapillary-api\\data\\metadata\\1.json', 'r') as file:
    data = json.load(file)

# Filter out panoramic images
filtered_features = [feature for feature in data['features'] if not feature['properties']['is_pano']]

# Update the data with filtered features
data['features'] = filtered_features

# Write the filtered data back to the file
with open('C:\\svi\\mapillary-api\\data\\metadata\\1_filtered.json', 'w') as file:
    json.dump(data, file, indent=4)

print(f"Filtered data saved to 1_filtered.json")