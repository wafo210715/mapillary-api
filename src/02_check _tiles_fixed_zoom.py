import mercantile
import folium

# Create a map centered on Chichester
m = folium.Map(location=[50.85, -0.78], zoom_start=14)

# amsterdan经纬度: [4.8896, 52.3576, 4.9186, 52.3776]
# chichester经纬度: [-0.805, 50.800, -0.738, 50.897]
west, south, east, north = [4.8896, 52.3576, 4.9186, 52.3776]
tiles = list(mercantile.tiles(west, south, east, north, 16))


for tile in tiles:
    bounds = mercantile.bounds(tile)
    folium.Rectangle(
        bounds=[(bounds.south, bounds.west), (bounds.north, bounds.east)],
        color="red", weight=1
    ).add_to(m)

m.save("amsterdam_tiles_16.html")