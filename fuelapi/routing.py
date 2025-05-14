import requests
import os
from dotenv import load_dotenv

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")


def get_route(start, finish):
    geocode_url = "https://api.openrouteservice.org/geocode/search"

    def geocode(location):
        params = {"api_key": ORS_API_KEY, "text": location, "boundary.country": "US"}
        resp = requests.get(geocode_url, params=params)
        resp.raise_for_status()
        coords = resp.json()["features"][0]["geometry"]["coordinates"]
        return coords  # [lon, lat]

    start_coords = geocode(start)
    end_coords = geocode(finish)

    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY}
    params = {
        "start": f"{start_coords[0]},{start_coords[1]}",
        "end": f"{end_coords[0]},{end_coords[1]}",
    }

    resp = requests.get(directions_url, headers=headers, params=params)
    resp.raise_for_status()
    # return resp.json()
    return {
        "route": resp.json(),
        "start_coords": start_coords[::-1],  # [lat, lon]
        "end_coords": end_coords[::-1],  # [lat, lon]
    }
