import pandas as pd

df = pd.read_csv("../../datasets/postal_code_part_1.csv")

# Replace invalid geocodes with None
df.loc[df["lat"] > 2, ["lat", "lon"]] = None

# Save cleaned data
df.to_csv("../../datasets/postal_code_part_1.csv", index=False)

print("done")