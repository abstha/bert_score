# run_bertscore_on_csv.py
# Usage:
#   python run_bertscore_on_csv.py --in pairs.csv --lang en --model roberta-large
import argparse, pandas as pd
from bert_score import score as bertscore

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="CSV with columns: candidate,reference")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--model", default=None, help="e.g., roberta-large (optional)")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    cands = df["candidate"].astype(str).tolist()
    refs  = df["reference"].astype(str).tolist()

    kw = {"lang": args.lang}
    if args.model:
        kw["model_type"] = args.model

    P, R, F1 = bertscore(cands=cands, refs=refs, **kw)

    out = df.copy()
    out["P"]  = [float(x) for x in P]
    out["R"]  = [float(x) for x in R]
    out["F1"] = [float(x) for x in F1]
    out_path = args.inp.replace(".csv", "_with_bertscore.csv")
    out.to_csv(out_path, index=False)
    print("Saved:", out_path)
    print(out.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
