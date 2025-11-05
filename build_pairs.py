import pandas as pd

df = pd.read_csv("en_ne_template.csv")   # your current file
pairs = df.rename(columns={"english":"candidate","nepali":"reference"})[["candidate","reference"]]
pairs.to_csv("pairs_crosslingual.csv", index=False)
print("✅ Saved pairs_crosslingual.csv with", len(pairs), "rows.")