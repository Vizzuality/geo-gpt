from flask import Blueprint, request, jsonify, session, render_template
from blueprints.geocode import get_geojson
from blueprints.analyze import get_land_cover_stats
from blueprints.describe import get_description
from blueprints.oauth import login_required
import ee
import json
import os

routes = Blueprint('routes', __name__)

print("Before ee.Initialize()")

service_account_key_path = "/home/ubuntu/shared/google_service.json"

# with open(service_account_key_path) as f:
#     service_account_info = json.load(f)

# credentials = ee.ServiceAccountCredentials(service_account_info['client_email'], service_account_key_path)
# ee.Initialize(credentials)

ee.Initialize()
print("After ee.Initialize()")

print("Earth Engine initialization in app.py:", ee.data._initialized)

@routes.route('/')
@login_required
def index():
    return render_template('index.html')

# @routes.route('/login')
# def login():
#     return render_template('login.html')

@routes.route('/geocode', methods=['POST'])
@login_required
def geocode():
    data = request.get_json()
    place = data.get("place")

    if not place:
        return jsonify({"error": "Place is required"}), 400

    geojson = get_geojson(place)
    if not geojson:
        return jsonify({"error": "Unable to get the geometry for the given place"}), 400

    return jsonify(geojson)



@routes.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    geojson = data.get("geometry")

    if not geojson:
        return jsonify({"error": "GeoJSON geometry is required"}), 400

    aoi = ee.Geometry.Polygon(geojson["coordinates"])
    result = get_land_cover_stats(aoi)

    if "error" in result:
        return jsonify({"error": "Unable to analyze the area"}), 400

    return jsonify(result)


@routes.route('/describe', methods=['POST'])
@login_required
def describe():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Data is required"}), 400

    stats = data.get('stats')
    text = data.get('text')

    result = get_description(stats, text)
    
    if "error" in result:
        return jsonify({"error": "Unable to generate description"}), 400

    return jsonify({"description": result})
