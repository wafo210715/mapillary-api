import folium

# Amsterdam bounding box coordinates
amsterdam = [4.8896, 52.3576, 4.9186, 52.3776]
west, south, east, north = amsterdam

# Create a map centered on Amsterdam
m = folium.Map(location=[(south + north) / 2, (west + east) / 2], zoom_start=13)

# Add a rectangle for the bounding box
folium.Rectangle(
    bounds=[[south, west], [north, east]],
    color='red',
    fill=True,
    fill_color='red',
    fill_opacity=0.2
).add_to(m)

# Save the map
m.save("amsterdam_bounding_box.html")

print("Map saved as amsterdam_bounding_box.html")