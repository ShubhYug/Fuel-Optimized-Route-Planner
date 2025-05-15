# Fuel-Optimized Route Planner

The Fuel-Optimized Route Planner is a Python-based web application that calculates driving routes between two U.S. cities, identifies the most cost-effective fuel stops along the way, estimates fuel consumption and total cost, and provides a link to view the route on Google Maps.

### ✨ Features
📍 Route Calculation
Uses the OpenRouteService API to calculate optimized driving routes.

⛽ Fuel Station Optimization
Finds nearby fuel stations along the route and picks the cheapest option within a configurable radius.

💰 Fuel Cost Estimation
Estimates total fuel consumption and cost based on vehicle MPG and fuel prices from a CSV file.

🗺️ Google Maps Integration
Provides a direct link to view the calculated route and fuel stops on Google Maps.

⚙️ Environment-Based Configuration
Set parameters like fuel range, MPG, and search radius using a .env file.

🧾 CSV Handling
Loads and geocodes fuel station data from a CSV file, with optional caching for faster performance.



## Technologies Used
1. Python 3

2. FastAPI or Django (depending on your setup)

3. OpenRouteService API

4. Google Maps link generation

5. Geopy (geocoding)

6. Pandas (CSV and data handling)

7. Haversine (distance calculations)

8. python-dotenv (for managing .env configs)
## Installation

1. Create an account for map and routing services and obtain the API key.

```
https://openrouteservice.org/dev/#/signup
```
2. Create virtual env

```bash
cd project/
python3 -m venv env
source env/bin/activate
```
3. Install depndance
```bash
pip install -r requirements.txt
```
4. Create ".env"
```bash
ORS_API_KEY=openrouteservice_api_key
FUEL_RANGE_MILES=500
MPG=10
FUEL_STOP_RADIUS_MILES=200
```

4. Run server

```bash
python3 manage.py run server
```

5. Docker (optional)

```bash
docker compose up --build
```
6. Now, you can access the app at
```bash
http://127.0.0.1:8000/api/
```