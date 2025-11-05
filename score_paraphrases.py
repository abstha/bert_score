# score_paraphrases.py
# Run: python score_paraphrases.py --in synonym_paraphrase_dataset.csv --model roberta-large

import argparse
import pandas as pd
from bert_score import score as bertscore

# ---- argument parser ----
ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", required=True,
                help="CSV file with columns: candidate,reference")
ap.add_argument("--model", default="roberta-large",
                help="HuggingFace model (default: roberta-large)")
ap.add_argument("--baseline", action="store_true",
                help="Use rescale_with_baseline=True (optional)")
args = ap.parse_args()

# ---- load data ----
df = pd.read_csv(args.inp)
cands = df["candidate"].astype(str).tolist()
refs  = df["reference"].astype(str).tolist()

# ---- run BERTScore ----
params = {"model_type": args.model}
if args.baseline:
    params["rescale_with_baseline"] = True  # optional calibration

print(f"Scoring {len(df)} pairs with model: {args.model} ...")
P, R, F1 = bertscore(cands=cands, refs=refs, **params)

# ---- save + print ----
df["P"]  = [float(x) for x in P]
df["R"]  = [float(x) for x in R]
df["F1"] = [float(x) for x in F1]

out_file = args.inp.replace(".csv", "_with_bertscore.csv")
df.to_csv(out_file, index=False)

print("\n✅ Done!")
print(" Mean Precision:", df["P"].mean())
print(" Mean Recall   :", df["R"].mean())
print(" Mean F1       :", df["F1"].mean())
print("\nResults saved to:", out_file)
