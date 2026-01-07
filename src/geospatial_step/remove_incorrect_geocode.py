"""
This script is to remove incorrect coordinates obtained from google maps.
Singapore's coordinates is within latitude of 1.05 - 1.5, longitude of 103.6 - 104.1
"""

import pandas as pd

# df = pd.read_csv("../../datasets/2unknown_postal_to_coordinate_results.xlsx")
df = pd.read_excel("../../datasets/2unknown_postal_to_coordinate_results.xlsx")

# Replace invalid geocodes with None. lat of Singapore cannot be more than 1.5 and less than 1.05
df.loc[df["lat"] > 1.5, ["lat", "lon"]] = None
df.loc[df["lat"] < 1.05, ["lat", "lon"]] = None

# Save cleaned data
df.to_excel("../../datasets/2unknown_postal_to_coordinate_results.xlsx")
# merged_postal_code_unknown.to_excel("../../datasets/testing_unknown_postal_code.xlsx")

print("done")