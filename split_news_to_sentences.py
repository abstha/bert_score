# split_news_to_sentences.py
# Usage: python split_news_to_sentences.py --in news.csv --out news_sentences.csv --max_per_article 4
import argparse, re, pandas as pd

def split_sentences(s: str):
    s = re.sub(r"\s+", " ", str(s)).strip()
    parts = re.split(r'(?<=[.!?])\s+', s)
    return [p.strip() for p in parts if p and len(p.strip()) > 0 and len(p.strip()) < 400]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--max_per_article", type=int, default=4)
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    rows = []
    for _, r in df.iterrows():
        sents = split_sentences(r["text"])[:args.max_per_article]
        for i, s in enumerate(sents):
            rows.append({
                "id": f"{r['id']}_{i}",
                "source": r["source"],
                "url": r["url"],
                "title": r["title"],
                "published": r["published"],
                "english": s
            })
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"Saved {len(out)} sentences to {args.out}")
    print(out.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
