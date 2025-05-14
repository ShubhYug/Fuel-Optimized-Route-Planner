from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .routing import get_route
from .fuel_optimizer import load_stations, get_fuel_stops

from django.shortcuts import render


def route_form_page(request):
    return render(request, "route.html")


@api_view(["POST"])
def route_view(request):
    """
    Calculate a route between two locations and determine optimal fuel stops.
    Expects JSON payload: { "start": "City, State", "finish": "City, State" }
    """
    start = request.data.get("start")
    finish = request.data.get("finish")

    if not start or not finish:
        return Response(
            {"error": "Missing 'start' or 'finish' location."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        route_data = get_route(start, finish)

        route_coords = route_data["route"]["features"][0]["geometry"]["coordinates"]

        start_coords = route_data["start_coords"]
        end_coords = route_data["end_coords"]

        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={start_coords[0]},{start_coords[1]}&destination={end_coords[0]},{end_coords[1]}"

        # Extract distance and duration
        summary = route_data["route"]["features"][0]["properties"]["summary"]
        distance_meters = summary["distance"]
        duration_seconds = summary["duration"]

        # Convert units
        distance_miles = round(distance_meters * 0.000621371, 2)
        # duration_hour = duration_seconds / 3600
        # duration_hours = round(duration_hour, 2)
        hours = duration_seconds // 3600  # Get the whole hours
        minutes = (duration_seconds % 3600) % 60 / 60
        duration_hours = hours + minutes

    except Exception as e:
        return Response(
            {"error": f"Error fetching route: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        # breakpoint()
        stations_df = load_stations()
        fuel_stops, total_cost = get_fuel_stops(route_coords, stations_df)
    except Exception as e:
        return Response(
            {"error": f"Error optimizing fuel stops: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            # "route": route_coords,
            "start": start,
            "finish": finish,
            "distance_miles": distance_miles,
            "duration_hours": round(duration_hours, 2),
            "total_fuel_cost_usd": round(total_cost, 2),
            "google_maps_link": maps_url,
            "fuel_stops": fuel_stops,
        }
    )
