from geopy.geocoders import Nominatim
from geopy import distance
from flask import Blueprint
import requests
from shapely.geometry import Point, mapping
from shapely.ops import transform
import pyproj

geocode_bp = Blueprint('geocode', __name__)

geolocator = Nominatim(user_agent='geo-gpt')

def create_buffer(lon, lat, buffer_distance):
    point = Point(lon, lat)
    
    # Define the projections for the transformation
    proj_in = pyproj.Proj(init='epsg:4326')  # WGS84
    proj_out = pyproj.Proj(init='epsg:3857')  # Web Mercator
    
    # Define the transformation function
    project = pyproj.Transformer.from_proj(proj_in, proj_out)
    project_reverse = pyproj.Transformer.from_proj(proj_out, proj_in)

    # Transform the point to Web Mercator and create a buffer
    point_web_mercator = transform(project.transform, point)
    buffer_web_mercator = point_web_mercator.buffer(buffer_distance)

    # Transform the buffer back to WGS84
    buffer_wgs84 = transform(project_reverse.transform, buffer_web_mercator)

    # Convert the buffer geometry to a GeoJSON-like dictionary
    buffer_geojson = mapping(buffer_wgs84)

    return buffer_geojson

def get_geojson(place):
    location = geolocator.geocode(place)
    if not location:
        return None

    osm_id = location.raw["osm_id"]
    osm_type = location.raw["osm_type"][0].upper()

    url = f"https://nominatim.openstreetmap.org/reverse?format=geojson&osm_type={osm_type}&osm_id={osm_id}&polygon_geojson=1"
    response = requests.get(url)
    data = response.json()

    if data['features']:
        region_geometry = data['features'][0]['geometry']

        # If the geometry is a Point, create a buffer around it
        if region_geometry["type"] == "Point":
            lon, lat = region_geometry["coordinates"]
            buffer_distance = 1000  # Define the buffer distance in meters
            buffered_geojson = create_buffer(lon, lat, buffer_distance)
            return buffered_geojson
        else:
            return region_geometry
    else:
        return None
