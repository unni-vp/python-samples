import folium
import pandas

def generate_volcano_map():

    """ Utility method to return color code based on volcano elevation """

    # Read the file containing volcano information
    volcano_data = pandas.read_csv("Volcanoes.txt")

    latitude_list = list(volcano_data["LAT"])
    longitude_list = list(volcano_data["LON"])
    volcano_names = list(volcano_data["NAME"])
    volcano_elevations = list(volcano_data["ELEV"])

    # Define Folium map with 'Stamen Terrain' tiles.
    map = folium.Map(location=[40,-110], zoom_start=5, tiles="Stamen Terrain")

    # Create feature group containig volcation locations and popup information
    volcano_grp = folium.FeatureGroup(name="Volcanoes")
    html = """<h4>Volcano Information:</h4><br/>Name: %s<br/>Height: %s m"""
    for lat, lon, name, el in zip(latitude_list, longitude_list, volcano_names, volcano_elevations):
        iframe = folium.IFrame(html=html % (name, str(el)), width=200, height=100)
        volcano_grp.add_child(folium.Marker(location=[lat, lon], popup=folium.Popup(iframe), icon=folium.Icon(color=get_color_for_elevation(el))))

    # Create feature group for displaying color-coded polygons for countries based on population
    geo_grp = folium.FeatureGroup(name="Population")
    geo_grp.add_child(folium.GeoJson(data=open('world.json', 'r', encoding="utf-8-sig").read(),
        style_function=lambda x: {'fillColor':'green' if x['properties']['POP2005'] < 2000000
        else 'red' if x['properties']['POP2005'] > 4000000 else 'orange'}))

    # Add feature groups and layer control. Layer control helps in switching features from the map view.
    map.add_child(volcano_grp)
    map.add_child(geo_grp)
    map.add_child(folium.LayerControl())

    # Save the map information to HTML file.
    map.save("volcano-map.html")


def get_color_for_elevation(elevation):

    """ Utility method to return color code based on volcano elevation """

    if elevation > 3000:
        return 'darkred'
    elif elevation > 2000:
        return 'red'
    elif elevation < 1000:
        return 'green'
    else:
        return 'orange'

# Generate the Volcano map on execution
generate_volcano_map()