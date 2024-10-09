import folium
from math import cos, radians

# Function to create a square bounding box
def create_square_bbox(center_lat, center_lon, side_length_m):
    # Approximate conversions
    # 1 degree of latitude is approximately 111,111 meters
    # 1 degree of longitude varies, but at Amsterdam's latitude it's about 69,400 meters
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
bbox_300m = create_square_bbox(amsterdam_center[0], amsterdam_center[1], 300)
bbox_1000m = create_square_bbox(amsterdam_center[0], amsterdam_center[1], 1000)
bbox_3000m = create_square_bbox(amsterdam_center[0], amsterdam_center[1], 3000)
bbox_10000m = create_square_bbox(amsterdam_center[0], amsterdam_center[1], 10000)

# Create a map centered on Amsterdam
m = folium.Map(location=amsterdam_center, zoom_start=11)

# Function to add a bounding box to the map
def add_bbox_to_map(m, bbox, color, label):
    west, south, east, north = bbox
    folium.Rectangle(
        bounds=[[south, west], [north, east]],
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.2,
        popup=label
    ).add_to(m)

# Add bounding boxes to the map
add_bbox_to_map(m, bbox_300m, 'red', '300m x 300m')
add_bbox_to_map(m, bbox_1000m, 'blue', '1000m x 1000m')
add_bbox_to_map(m, bbox_3000m, 'green', '3000m x 3000m')
add_bbox_to_map(m, bbox_10000m, 'purple', '10000m x 10000m')

# Add a marker for the center of Amsterdam
folium.Marker(
    amsterdam_center,
    popup='Amsterdam Center',
    icon=folium.Icon(color='black', icon='info-sign')
).add_to(m)

# Save the map
m.save("amsterdam_bounding_boxes.html")

print("Map saved as amsterdam_bounding_boxes.html")