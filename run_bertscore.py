import pandas as pd
from bert_score import score as bertscore

df = pd.read_csv("pairs_crosslingual.csv")   # or pairs_clean.csv if you renamed it
cands = df["candidate"].astype(str).tolist()
refs  = df["reference"].astype(str).tolist()

print("🔍 Scoring", len(df), "sentence pairs...")

# multilingual model for EN↔NE comparison
P, R, F1 = bertscore(cands=cands, refs=refs, model_type="xlm-roberta-large")

df["P"] = [float(x) for x in P]
df["R"] = [float(x) for x in R]
df["F1"] = [float(x) for x in F1]
df.to_csv("pairs_with_bertscore.csv", index=False)

print("\n✅ Done! Saved results to pairs_with_bertscore.csv\n")
print("📌 Mean Scores:")
print(" Precision:", df["P"].mean())
print(" Recall:", df["R"].mean())
print(" F1:", df["F1"].mean())
