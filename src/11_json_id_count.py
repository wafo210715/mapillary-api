import json

# Open and parse the JSON file
with open(r'C:\svi\mapillary-api\data\metadata\1_filtered.json', 'r') as file:
    data = json.load(file)

# Extract all 'id' values from the 'properties' of each feature
ids = [feature['properties']['id'] for feature in data['features']]

# Count unique ids
unique_ids_count = len(set(ids))

print(f"Number of unique 'id' values: {unique_ids_count}")