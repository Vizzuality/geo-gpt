import os
from flask import Blueprint
import ee

analyze_bp = Blueprint('analyze', __name__)

def geojson_to_ee(geojson):
    return ee.Geometry(geojson)

def get_land_cover_stats(aoi_geojson):
    aoi = geojson_to_ee(aoi_geojson)

    collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    filtered_collection = collection.filterBounds(aoi)
    land_cover = filtered_collection.mosaic().clip(aoi)

    legend = {
        "items": [
            {"name": "Water", "color": "#419BDF", "id": 0, "band": "water"},
            {"name": "Trees", "color": "#397D49", "id": 1, "band": "trees"},
            {"name": "Grass", "color": "#88B053", "id": 2, "band": "grass"},
            {"name": "Flooded Vegetation", "color": "#7A87C6", "id": 3, "band": "flooded_vegetation"},
            {"name": "Crops", "color": "#E49635", "id": 4, "band": "crops"},
            {"name": "Shrub and Scrub", "color": "#DFC35A", "id": 5, "band": "shrub_and_scrub"},
            {"name": "Built", "color": "#C4281B", "id": 6, "band": "built"},
            {"name": "Bare", "color": "#A59B8F", "id": 7, "band": "bare"},
            {"name": "Snow and Ice", "color": "#B39FE1", "id": 8, "band": "snow_and_ice"},
        ]
    }


    stats = {}
    map_tile_url = ""

    try:
        for item in legend['items']:
            class_id = item['id']
            class_name = item['name']
            band = item['band']
            print(f"Processing {class_id}: {class_name} ({band})")
            mask = land_cover.select(band)
            class_area = mask.multiply(ee.Image.pixelArea()).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=aoi,
                scale=10,
                maxPixels=1e9,
                bestEffort=True,
            )

            class_area_hectares = ee.Number(class_area.get(band)).divide(10000)
            stats[band] = {
                "name": item["name"],
                "area": round(class_area_hectares.getInfo(), 2),
            }

        map_tile_url = land_cover.getMapId()["tile_fetcher"].url_format
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

    return {"stats": stats, "map_tile_url": map_tile_url}