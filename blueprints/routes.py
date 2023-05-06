import ee
import json
import os
from flask import Blueprint, request, jsonify, session, render_template, send_from_directory, current_app
from blueprints.geocode import get_geojson
from blueprints.analyze import get_land_cover_stats
from blueprints.describe import get_description
from blueprints.conditional_login_required import conditional_login_required
from config import service_account_key_path

routes = Blueprint('routes', __name__)

print("Before ee.Initialize()")

with open(service_account_key_path) as f:
    service_account_info = json.load(f)

credentials = ee.ServiceAccountCredentials(service_account_info['client_email'], service_account_key_path)
ee.Initialize(credentials)

#ee.Initialize()
print("After ee.Initialize()")

print("Earth Engine initialization in app.py:", ee.data._initialized)

@routes.route("/robots.txt")
def robots_txt():
    return send_from_directory(current_app.root_path, "robots.txt")

@routes.route('/')
@conditional_login_required
def index():
    return render_template('index.html')

# @routes.route('/login')
# def login():
#     return render_template('login.html')

@routes.route('/geocode', methods=['POST'])
@conditional_login_required
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
@conditional_login_required
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
@conditional_login_required
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
