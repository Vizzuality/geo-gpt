from math import log, tan, radians, cos, pi, floor, degrees, atan, sinh
from geopy.geocoders import Nominatim
from geopy import distance
from flask import Blueprint

geocode_bp = Blueprint('geocode', __name__)


geolocator = Nominatim(user_agent='geo-gpt')

def sec(x):
    return(1/cos(x))


def latlon_to_xyz(lat, lon, z):
    tile_count = pow(2, z)
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return(tile_count*x, tile_count*y)

def bbox_to_xyz(min_lon, max_lon, min_lat, max_lat, z):
    x_min, y_max = latlon_to_xyz(min_lat, min_lon, z)
    x_max, y_min = latlon_to_xyz(max_lat, max_lon, z)
    return(floor(x_min), floor(x_max),
           floor(y_min), floor(y_max))


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

