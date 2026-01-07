"""
To convert from postal codes to coordinates (lat and long) so that OHCA occurances can be plotted
googlemaps package will need to be installed using either PIP, CONDA etc...
API_KEY of google maps will need to be generated with a google cloud account. 
"""

import pandas as pd
import openpyxl
from dotenv import load_dotenv
import os
import time
import googlemaps

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))

load_dotenv(os.path.join(parent_dir, ".env"))

API_KEY = os.getenv("API_KEY")
gmaps = googlemaps.Client(key = API_KEY)

filepath = "../../datasets/postal_code_data/remaining_postalcodes.xlsx"

postalcode = pd.read_excel(filepath, sheet_name = 0)

def geocode_address(address, retries: int = 2, sleep: float = 0.2):
    if not isinstance(address, str) or not address.strip():
        return None
    query = address.strip()

    for _ in range(retries):
        try:
            geocoded_results = gmaps.geocode(query)
            if geocoded_results:
                return geocoded_results[0]["geometry"]["location"]
            return None
        except Exception as e:
            last_error = e
            time.sleep(sleep)
    print(f"Geocoding failed for '{address}': {last_error}")
    return None


output_path = "../../datasets/postal_code_data/translated_remaining_postalcodes.xlsx"

records = []
final_output = pd.DataFrame()
for address in postalcode["Location Type Other"].fillna(""):
    location = geocode_address(address)
    records.append({
        "Address": address,
        "lat": location["lat"] if location else None,
        "lon": location["lng"] if location else None,
    })
    time.sleep(0.1)
    # coordinate = geocode_address(address)
    # # coordinate = {'lat': 1.306591, 'lng': 103.898422}
    # address_dict = {"Address": address}
    # coordinate.update(address_dict)
    # df_dict = pd.DataFrame([coordinate])
    # final_output = pd.concat([final_output, df_dict], ignore_index = True)

postalcode = pd.DataFrame(records, columns = ["Address", "lat", "lon"])
postalcode.to_excel(output_path)
# final_output.to_excel(output_path)

