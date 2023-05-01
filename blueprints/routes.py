from flask import Blueprint, request, jsonify, session, render_template
#from blueprints.auth import token_auth
from blueprints.geocode import get_bbox
from blueprints.analyze import get_land_cover_stats
from blueprints.describe import get_description
from blueprints.oauth import login_required
import ee

routes = Blueprint('routes', __name__)

print("Before ee.Initialize()")
ee.Initialize()
print("After ee.Initialize()")
print("Earth Engine initialization in app.py:", ee.data._initialized)

@routes.route('/')
@login_required
def index():
    return render_template('index.html')

@routes.route('/geocode', methods=['POST'])
#@token_auth.login_required
def geocode():
    data = request.get_json()
    place = data.get("place")

    if not place:
        return jsonify({"error": "Place is required"}), 400

    bbox = get_bbox(place)
    return jsonify(bbox)

@routes.route('/analyze', methods=['POST'])
#@token_auth.login_required
def analyze():
    data = request.get_json()
    min_lat = data.get("min_lat")
    max_lat = data.get("max_lat")
    min_lon = data.get("min_lon")
    max_lon = data.get("max_lon")

    if not all([min_lat, max_lat, min_lon, max_lon]):
        return jsonify({"error": "All coordinates (min_lat, max_lat, min_lon, max_lon) are required"}), 400

    aoi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
    stats = get_land_cover_stats(aoi)

    return jsonify(stats)

@routes.route('/describe', methods=['POST'])
def describe():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Data is required"}), 400

    stats = data.get('stats')
    text = data.get('text')

    description = get_description(stats, text)

    return jsonify({"description": description})
