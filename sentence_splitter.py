# sentence_splitter.py
# Usage:
#   python sentence_splitter.py --in data/news.csv --out data/news_sentences.csv --max_per_article 4
import argparse, re, pandas as pd

def split_sentences(text: str):
    # naive split: . ? ! followed by space
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p and len(p.strip()) > 0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--max_per_article", type=int, default=4)
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    rows = []
    for _, r in df.iterrows():
        sents = split_sentences(str(r.get("text", "")))[:args.max_per_article]
        for i, s in enumerate(sents):
            rows.append({
                "id": f"{r.get('id','')}_{i}",
                "source": r.get("source", ""),
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "sentence": s
            })
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"Saved {len(out)} sentences to {args.out}")
    print(out.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
