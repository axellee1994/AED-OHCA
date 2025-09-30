import pandas as pd
from sqlalchemy import create_engine

import os
print(os.getcwd())

# Read CSV
df = pd.read_csv("../penang_ambulance/datasets/penang_ems_cleaned_at_scene.csv")

# Connect to Postgres (needa adjust credentials)
engine = create_engine("postgresql://yitong@localhost:5432/penang_ems")

# Write to DB (creates table automatically)
df.to_sql("scene_points", engine, if_exists="replace", index=False)