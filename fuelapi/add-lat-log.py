import pandas as pd
import openrouteservice
from time import sleep

API_KEY = "5b3ce3597851110001cf6248481c69f420244ed0913dfc8b5d997783"  # <-- Replace with your actual API key
client = openrouteservice.Client(key=API_KEY)


def geocode_ors(row):
    try:
        query = f"{row['Address']}, {row['City']}, {row['State']}"
        result = client.pelias_search(text=query)
        coords = result["features"][0]["geometry"]["coordinates"]
        return pd.Series({"longitude": coords[0], "latitude": coords[1]})
    except Exception as e:
        print(f"Error geocoding: {query} — {e}")
        return pd.Series({"longitude": None, "latitude": None})


# Read your original CSV
df = pd.read_csv("fuel-prices-for-be-assessment.csv")

# Add lat/lon using ORS
geo = df.apply(geocode_ors, axis=1)
df[["longitude", "latitude"]] = geo

# Save the new file
df.to_csv("fuel-stations-with-coords.csv", index=False)
print("✅ Geocoding completed and file saved as 'fuel_prices_with_latlon.csv'")
