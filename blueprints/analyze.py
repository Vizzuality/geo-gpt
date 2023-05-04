import os
from flask import Blueprint
import ee


analyze_bp = Blueprint('analyze', __name__)

def geojson_to_ee(geojson):
    return ee.Geometry(geojson)

def map_results(key, legend):
    filtered = list(filter(lambda _dict: str(_dict.get('id')) == key, legend.get("items", [])))
    if len(filtered) > 0:
        return filtered[0].get("name")
    else:
        print("No matching legend item found for key: {}".format(key))
        


def get_land_cover_stats(aoi_geojson):
    
    aoi = geojson_to_ee(aoi_geojson)

    collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    filtered_collection = collection.filterBounds(aoi)
    land_cover = filtered_collection.select('label').reduce(ee.Reducer.mode()).clip(aoi)
    probabilityBands = [
    'water', 'trees', 'grass', 'flooded_vegetation', 'crops', 'shrub_and_scrub',
    'built', 'bare', 'snow_and_ice'
        ];
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
    keys = [str(item["id"]) for item in legend["items"]]
    labels = [item["band"] for item in legend["items"]]
    
    # ee.Reducer.sum()
    reducer = {
        "reducer": ee.Reducer.frequencyHistogram().unweighted(),
        "geometry": aoi,
        "scale":10,
        "maxPixels": 1e16,
        "bestEffort": True,
        "tileScale": 16,
    }
    stats = {}
    map_tile_url = ""
    visual_params = {
        "bands": ["label_mode"],
        "min": 0,
        "max": 8,
        "opacity": 1,
        "palette": [item["color"] for item in legend["items"]],
        "forceRgbOutput": True,
    }
    # .select(probabilityBands).multiply(ee.Image.pixelArea()).divide(10000)
    try:
        class_area = ee.Dictionary(land_cover.reduceRegion(**reducer).get('label_mode')).getInfo()
        print(class_area)
        stats = { k:{"area": round(v*10*10/10000.0, 2), "name": map_results(k, legend)} for k, v in class_area.items()}
        map_tile_url = land_cover.visualize(**visual_params).getMapId()["tile_fetcher"].url_format


        return {"stats": stats, "map_tile_url": map_tile_url}
    
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}