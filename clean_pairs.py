# repair_and_clean_pairs.py
# 1) Robustly parse a 2-column CSV where both fields contain commas but aren't quoted,
#    by splitting at the comma *right before* Nepali (Devanagari) starts.
# 2) Clean obvious noise, save a proper quoted CSV for pandas.
import re, pandas as pd, sys, io

INPUT = "pairs_crosslingual.csv"     # change if your filename is different
REPAIRED = "pairs_repaired.csv"
CLEANED = "pairs_clean.csv"

# Regex: candidate (anything), comma, spaces, then reference that starts with Nepali char
LINE_RE = re.compile(r'^(?P<cand>.*?),\s*(?P<ref>[\u0900-\u097F].+)$')

# --- Step 1: read raw lines, repair into two columns ---
rows = []
with open(INPUT, "r", encoding="utf-8") as f:
    header = f.readline()  # expect "candidate,reference"
    for i, raw in enumerate(f, start=2):
        line = raw.rstrip("\n")
        m = LINE_RE.match(line)
        if not m:
            # skip blank/garbage lines quietly; print if you need to debug:
            # print(f"Skipping line {i}: {line[:120]}")
            continue
        cand = m.group("cand").strip()
        ref = m.group("ref").strip()
        rows.append({"candidate": cand, "reference": ref})

if not rows:
    sys.exit("No rows parsed. Check the input filename or contents.")

df = pd.DataFrame(rows)
# Save a proper CSV with quotes so pandas can read it later without issues
df.to_csv(REPAIRED, index=False)
print(f"✅ Repaired {len(df)} rows -> {REPAIRED}")

# --- Step 2: light cleaning (same logic as before, compact) ---
def clean_en(s: str) -> str:
    s = str(s)
    s = re.sub(r'^\s*(Please let us know|Find any issues)[^,.!?]*[,.!?]?\s*', '', s, flags=re.I)
    s = re.sub(r'\([^)]{0,120}\)', ' ', s)
    s = s.replace('“','"').replace('”','"').replace("’","'")
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_ne(s: str) -> str:
    s = str(s)
    s = re.sub(r'\([^)]{0,120}\)', ' ', s)
    s = s.replace('“','"').replace('”','"').replace("’","'")
    s = re.sub(r'\s+', ' ', s).strip()
    # collapse exact back-to-back duplication: "X X"
    m = re.match(r'^(?P<x>.+?)\s*\1$', s)
    if m: s = m.group('x').strip()
    return s

def ok_len(s: str, lo=6, hi=40) -> bool:
    w = len(s.split())
    return lo <= w <= hi

df["candidate"] = df["candidate"].map(clean_en)
df["reference"] = df["reference"].map(clean_ne)
df = df[(df["candidate"].str.len() > 0) & (df["reference"].str.len() > 0)]
df = df[df["candidate"].map(ok_len) & df["reference"].map(ok_len)]
df = df.drop_duplicates()
df.to_csv(CLEANED, index=False)
print(f"✅ Cleaned {len(df)} rows -> {CLEANED}")
print(df.head(5).to_string(index=False))
