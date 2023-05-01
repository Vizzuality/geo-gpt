from math import log, tan, radians, cos, pi, floor, degrees, atan, sinh
from geopy.geocoders import Nominatim
from geopy import distance
from flask import Blueprint

geocode_bp = Blueprint('geocode', __name__)


geolocator = Nominatim(user_agent='geo-gpt')

def get_bbox(place, size=10):
    location = geolocator.geocode(place)
    if not location:
        return None 
    lat, lon = location.latitude, location.longitude
    lat_delta = distance.distance(kilometers=size).destination((lat, lon), bearing=0).latitude - lat
    lon_delta = distance.distance(kilometers=size).destination((lat, lon), bearing=90).longitude - lon

    min_lat, max_lat = lat - lat_delta, lat + lat_delta
    min_lon, max_lon = lon - lon_delta, lon + lon_delta

    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
    }

