import mercantile
import folium

# Create a map centered on Amsterdam
m = folium.Map(location=[52.3676, 4.9041], zoom_start=11)

# Amsterdam bounding box (approximate)
west, south, east, north = 4.7285, 52.2784, 5.0679, 52.4311

# Colors for different zoom levels
colors = ['red', 'blue', 'green', 'purple']

# Get tiles for zoom levels 11 to 14
for zoom in range(11, 15):
    tiles = list(mercantile.tiles(west, south, east, north, zoom))
    
    for tile in tiles:
        bounds = mercantile.bounds(tile)
        folium.Rectangle(
            bounds=[(bounds.south, bounds.west), (bounds.north, bounds.east)],
            color=colors[zoom - 11],
            weight=1,
            fill=True,
            fillColor=colors[zoom - 11],
            fill_opacity=0.1,
            opacity=0.5
        ).add_to(m)

m.save("amsterdam_tiles_11_14.html")