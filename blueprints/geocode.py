from math import log, tan, radians, cos, pi, floor, degrees, atan, sinh
from geopy.geocoders import Nominatim
from geopy import distance
from flask import Blueprint
import requests

geocode_bp = Blueprint('geocode', __name__)

geolocator = Nominatim(user_agent='geo-gpt')

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
        return region_geometry
    else:
        return None