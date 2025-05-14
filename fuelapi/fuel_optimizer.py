import pandas as pd
from haversine import haversine, Unit
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor
import os
import time


FUEL_RANGE_MILES = float(os.getenv("FUEL_RANGE_MILES"))
MPG = float(os.getenv("MPG"))
FUEL_STOP_RADIUS_MILES = float(os.getenv("FUEL_STOP_RADIUS_MILES"))
geolocator = Nominatim(user_agent="fuel_optimizer")


def get_fuel_stops(route_coords, stations_df):
    fuel_stops = []
    total_distance = 0
    fuel_cost = 0.0
    gallons_needed = 0.0

    print(f"Route has {len(route_coords)} segments")

    for i in range(len(route_coords) - 1):
        start = tuple(route_coords[i][::-1])
        end = tuple(route_coords[i + 1][::-1])
        dist = haversine(start, end, unit=Unit.MILES)
        total_distance += dist

        if total_distance >= FUEL_RANGE_MILES:
            print(
                f"\nNeed refuel after {total_distance:.2f} miles, checking near {start}..."
            )
            segment_center = start
            stations_df["distance"] = stations_df.apply(
                lambda row: haversine(segment_center, (row.latitude, row.longitude)),
                axis=1,
            )

            nearby = stations_df[stations_df["distance"] <= FUEL_STOP_RADIUS_MILES]

            print(f"Found {len(nearby)} stations within {FUEL_STOP_RADIUS_MILES} miles")

            if not nearby.empty:
                cheapest = nearby.sort_values("price_per_gallon").iloc[0]
                gallons = FUEL_RANGE_MILES / MPG
                cost = gallons * cheapest.price_per_gallon

                fuel_cost += cost
                gallons_needed += gallons
                fuel_stops.append(
                    {
                        "station_name": cheapest.station_name,
                        "location": [cheapest.latitude, cheapest.longitude],
                        "fuel_price": round(cheapest.price_per_gallon, 2),
                        "gallons": round(gallons, 2),
                        "cost": round(cost, 2),
                    }
                )
            else:
                print("No nearby station found for this segment!")

            total_distance = 0

    return fuel_stops, fuel_cost


# Load the original CSV without latitude and longitude
def load_stations():
    COORD_CSV = "fuel-stations-with-coords.csv"
    if os.path.exists(COORD_CSV):
        print(f"Loading cached station coordinates from {COORD_CSV}")
        df = pd.read_csv(COORD_CSV)
        print(f"Loaded {len(df)} stations with valid coordinates")
        return df[
            [
                "station_name",
                "City",
                "State",
                "price_per_gallon",
                "latitude",
                "longitude",
            ]
        ]

    # Load the original CSV with missing lat/lng
    df = pd.read_csv("fuel-prices-for-be-assessment.csv")

    # Remove duplicates and filter out incomplete rows
    df = df.drop_duplicates(subset=["Truckstop Name", "City", "State"])
    df = df.dropna(
        subset=["City", "State", "Truckstop Name"]
    )  # Remove rows with missing city, state, or station name

    # Standardize column names
    df = df.rename(
        columns={"Truckstop Name": "station_name", "Retail Price": "price_per_gallon"}
    )

    # Initialize the geolocator
    # geolocator = Nominatim(user_agent="fuel_optimizer")

    # Coordinate caching to avoid duplicate API calls
    coord_cache = {}

    # Geocode function to fetch lat/lon
    def get_lat_lon(station_name, city, state):
        key = f"{station_name.strip().lower()}_{city.strip().lower()}_{state.strip().lower()}"
        if key in coord_cache:
            return coord_cache[key]
        try:
            location = geolocator.geocode(
                f"{station_name}, {city}, {state}", timeout=10
            )
            if location:
                coord_cache[key] = (location.latitude, location.longitude)
                return coord_cache[key]
        except Exception as e:
            print(f"Geocoding error for {station_name}, {city}, {state}: {e}")
        coord_cache[key] = (None, None)
        return None, None

    # Function to process each row and get lat/lon
    def process_row(row):
        city = row["City"]
        state = row["State"]
        station_name = row["station_name"]
        if pd.isna(city) or pd.isna(state) or pd.isna(station_name):
            print(f"Skipping row due to missing data: {station_name}, {city}, {state}")
            return None, None
        lat, lon = get_lat_lon(station_name, city, state)
        return lat, lon

    # Parallel geocoding using ThreadPoolExecutor
    latitudes = []
    longitudes = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda row: process_row(row[1]), df.iterrows()))

    # Unzip lat/lon tuples and assign directly
    latitudes, longitudes = zip(*results)

    df["latitude"] = latitudes
    df["longitude"] = longitudes

    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     results = executor.map(lambda row: process_row(row), df.iterrows())

    # for lat, lon in results:
    #     if lat is not None and lon is not None:
    #         latitudes.append(lat)
    #         longitudes.append(lon)
    #     time.sleep(0.2)  # Slight delay to avoid overwhelming the geocoding API

    # df["latitude"] = latitudes
    # df["longitude"] = longitudes

    # Drop stations with failed geocoding
    df = df.dropna(subset=["latitude", "longitude"])

    # Save to cache for future runs
    df.to_csv(COORD_CSV, index=False)
    print(f"Geocoded and saved {len(df)} stations to {COORD_CSV}")

    return df[
        ["station_name", "City", "State", "price_per_gallon", "latitude", "longitude"]
    ]
