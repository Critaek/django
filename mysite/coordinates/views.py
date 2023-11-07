from django.shortcuts import render
from django.http import JsonResponse
import googlemaps
import json
import shapely
from typing import Optional, Tuple

def valid_lonlat(lon: float, lat: float) -> Optional[Tuple[float, float]]:
    """
    This validates a lat and lon point can be located
    in the bounds of the WGS84 CRS, after wrapping the
    longitude value within [-180, 180)

    :param lon: a longitude value
    :param lat: a latitude value
    :return: (lon, lat) if valid, None otherwise
    """
    lon %= 360
    if lon >= 180:
        lon -= 360
    lon_lat_point = shapely.geometry.Point(lon, lat)
    lon_lat_bounds = shapely.geometry.Polygon.from_bounds(
        xmin=-180.0, ymin=-90.0, xmax=180.0, ymax=90.0
    )

    if lon_lat_bounds.intersects(lon_lat_point):
        return lon, lat
    
def is_float_formatable(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

key = 'GoogleAPIKey'
url = 'https://places.googleapis.com/v1/places:searchNearby'
client = googlemaps.Client(key)
n_ret = 1

query = ["caffe", "cafe", "coffee"]
language = "en"

# Create your views here.
def index(request): 
    
    json_data = json.loads(request.body)
    lat = json_data.get("lat")
    lng = json_data.get("lng")
        
    if lat is None or lng is None or not is_float_formatable(lat) or not is_float_formatable(lng):
        return JsonResponse({"error": "lat or lng is either None or not a float"})
    
    if not valid_lonlat(float(lng), float(lat)):
        return JsonResponse({"error": "Coordinates not valid"})
    
    location = (lat, lng)
    r = client.places_nearby(
        location=location,
        keyword=query,
        language=language,
        open_now=True,
        rank_by="distance"
    )

    results = r.get("results")

    if n_ret == 1:
        return JsonResponse({"results": [{results[0].get("name"): results[0].get("geometry").get("location")}]})
    else:
        final = []
        for i in range(n_ret):
            result = results[i]
            name = result.get("name")
            location = result.get("geometry").get("location")

            final.append({"name": name, "location": location})

        final = {"results": final}

    return JsonResponse(final)