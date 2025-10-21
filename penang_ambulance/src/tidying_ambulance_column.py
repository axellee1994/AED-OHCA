import pandas as pd
import numpy as np
import re
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, parent_dir)

from src.helper_functions.helper_methods import query_distinct_values


distinct_ambulance = query_distinct_values("ambulance dispatched (tier 1)", "incidents")
print(distinct_ambulance)
print()

ambulance_df = pd.read_excel("penang_ambulance/datasets/penang_maps/ambulance_locations.xlsx", sheet_name = "unique_ambulances")
given_ambulance = ambulance_df["Ambulance Call Sign"].to_list()
given_ambulance = [call_sign.lower() for call_sign in given_ambulance]
print(given_ambulance)
print()

# ambulance_df = pd.read_csv("penang_ambulance/datasets/Processed_EMS_Calls_Penang_2024.csv")
# given_ambulance = ambulance_df["Ambulance Dispatched (Tier 1)"].to_list()
# # given_ambulance = [call_sign.lower() for call_sign in given_ambulance]
# am_am = list(set(given_ambulance))
# print(am_am)
# print()

# cleaned = {}
# for item in distinct_ambulance:
#     s = item.lower()
#     s = re.sub(r'\([^)]*\)', '', s)       # remove parentheses
#     s = re.sub(r'([a-z])(\d)', r'\1 \2', s)  # split letters+numbers (e.g., rc6 -> rc 6)
#     s = re.sub(r'(\d)([a-z])', r'\1 \2', s)  # split numbers+letters (e.g., bravo1 -> bravo 1)
#     s = re.sub(r'\s+', ' ', s).strip()   # normalize spaces
#     s = re.sub(r'\bst\.?\s*john\b', 'sj', s) # replace st. john with sj
#     s = s.replace(",", "")                 # remove commas
#     cleaned[item] = s

# print(cleaned)


