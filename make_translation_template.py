# make_translation_template.py
# Usage: python make_translation_template.py --in news_sentences.csv --out en_ne_template.csv --n 25
import argparse, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--n", type=int, default=25)
    args = ap.parse_args()

    df = pd.read_csv(args.inp).head(args.n)[["id","english","source","url","title"]]
    df["nepali"] = ""           # fill this column manually
    df["annotator"] = ""        # (optional) write your name/initials
    df.to_csv(args.out, index=False)
    print("Template written to", args.out)

if __name__ == "__main__":
    main()
