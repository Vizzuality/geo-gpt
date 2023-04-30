import os
from flask import Blueprint
import ee

analyze_bp = Blueprint('analyze', __name__)

def get_land_cover_stats(aoi):
    legend = {
        "items": [
        {"name": "Water", "color": "#419BDF", "id": 0},
        {"name": "Trees", "color": "#397D49", "id": 1},
        {"name": "Grass", "color": "#88B053", "id": 2},
        {"name": "Flooded Vegetation", "color": "#7A87C6", "id": 3},
        {"name": "Crops", "color": "#E49635", "id": 4},
        {"name": "Shrub and Scrub", "color": "#DFC35A", "id": 5},
        {"name": "Built", "color": "#C4281B", "id": 6},
        {"name": "Bare", "color": "#A59B8F", "id": 7},
        {"name": "Snow and Ice", "color": "#B39FE1", "id": 8},
        ]
    }

    collection = ee.ImageCollection("projects/wri-datalab/dynamicworld/rw/rgb/DW_202207")
    filtered_collection = collection.filterBounds(aoi)
    land_cover = filtered_collection.mosaic()
    land_cover = land_cover.clip(aoi)

    def hex_to_rgb(hex_color):
        return [int(hex_color[i:i+2], 16) for i in (1, 3, 5)]

    stats = {}

    for class_info in legend["items"]:
        class_id = class_info['id']
        class_color = ee.Image.constant(hex_to_rgb(class_info['color'])).toFloat()

        mask = land_cover.eq(class_color).reduce(ee.Reducer.allNonZero())

        class_area = mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi,
            scale=10,
            maxPixels=1e9
        )

        stats[class_id] = {
            "name": class_info["name"],
            "area": class_area.getInfo(),
        }

    return stats