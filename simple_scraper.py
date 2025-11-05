# scrape_simple.py
# Usage:
#   python scrape_simple.py --out data/news.csv --per_feed 12
import argparse, time, re, random, hashlib, os
from urllib.parse import urlparse

import requests, feedparser
from bs4 import BeautifulSoup
import pandas as pd

UA = {"User-Agent": "AbhinavStudentScraper/1.0 (research use)"}

DEFAULT_RSS = [
    "https://www.abc.net.au/news/feed/51120/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/au/rss",
]

def sha16(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

def get_links_from_rss(rss_url: str, limit: int | None = None):
    feed = feedparser.parse(rss_url)
    for i, e in enumerate(feed.entries):
        if limit and i >= limit: break
        yield {
            "link": getattr(e, "link", ""),
            "title": getattr(e, "title", ""),
            "published": getattr(e, "published", getattr(e, "updated", "")),
        }

def fetch(url: str, timeout=12):
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return None

def extract_text(html: str) -> tuple[str, str]:
    """Very simple extractor: page <title> and visible <p> text."""
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else ""
    parts = []
    for p in soup.find_all("p"):
        t = p.get_text(" ", strip=True)
        if len(t) > 40:            # skip short boilerplate
            parts.append(t)
    text = " ".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    return title, text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rss", nargs="+", default=DEFAULT_RSS)
    ap.add_argument("--per_feed", type=int, default=10)
    ap.add_argument("--out", type=str, default="news.csv")
    args = ap.parse_args()

    rows, seen = [], set()

    for rss in args.rss:
        for item in get_links_from_rss(rss, limit=args.per_feed):
            url = item["link"]
            if not url or url in seen:
                continue
            seen.add(url)

            html = fetch(url)
            if not html:
                continue

            title, text = extract_text(html)
            if len(text) < 200:     # probably not an article
                continue

            host = urlparse(url).netloc
            rid = sha16(url)
            rows.append({
                "id": rid,
                "source": host,
                "url": url,
                "title": item["title"] or title,
                "published": item["published"],
                "text": text
            })
            time.sleep(random.uniform(0.8, 1.6))   # polite pause

    if not rows:
        print("No rows scraped.")
        return

    df = pd.DataFrame(rows)
    out_dir = os.path.dirname(args.out) or "."
    os.makedirs(out_dir, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} rows to {args.out}")
    print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    main()
