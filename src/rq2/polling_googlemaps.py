import pandas as pd
import numpy as np
import geopandas as gpd
import time
from geopy.geocoders import Nominatim
import time

filename = "postal_code_part_1.csv"

postal_code_df = pd.read_csv("../../datasets/" + filename)

geolocator = Nominatim(
    user_agent="sg-incident-geocoder/1.0 (you@example.com)",
    timeout=10
)

def geocode_postal(code, country="sg"):
    """
    Look up a postal code with Nominatim.
    Returns (lat, lon) or (None, None) if not found.
    """
    location = geolocator.geocode(
        {"postalcode": str(code), "countrycodes": country, "limit": 1},
        exactly_one=True,
        addressdetails=False
    )
    return (location.latitude, location.longitude) if location else (None, None)

latitudes, longitudes = [], []
for pc in postal_code_df["postal code"]:
    lat, lon = geocode_postal(pc)
    latitudes.append(lat);  longitudes.append(lon)
    time.sleep(1.05)                       # ← 1 request / second (usage policy)

postal_code_df["lat"] = latitudes
postal_code_df["lon"] = longitudes

output_path = "../../datasets/" +  filename
postal_code_df.to_csv(output_path, index = False)

