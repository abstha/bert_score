import re
import pandas as pd
from datasets import load_dataset
from bert_score import score as bertscore

# --------- Config ----------
DATASET_NAME = "cnn_dailymail"
CONFIG = "3.0.0"           # standard config for CNN/DailyMail
SPLIT = "validation"       # small, quick to load; you can switch to "train"
N = 8                      # how many examples to process for the demo
OUTPUT_CSV = "cnn_dm_bertscore_demo.csv"
# ---------------------------

def clean_text(s: str) -> str:
    """
    Simple preprocessing:
    - collapse whitespace
    - remove weird unicode quotes/slashes
    - strip leading/trailing spaces
    Add/adjust rules as you like (but keep it simple for the update video)
    """
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[’]", "'", s)
    s = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", s)  # zero-width chars
    s = re.sub(r"\s+", " ", s).strip()
    return s

print("Loading dataset…")
ds = load_dataset(DATASET_NAME, CONFIG, split=SPLIT)

# Keep only the first N for a quick demo
ds_small = ds.select(range(min(N, len(ds))))

# CNN/DailyMail fields: article (source) and highlights (reference summary)
articles = [clean_text(x["article"]) for x in ds_small]
references = [clean_text(x["highlights"]) for x in ds_small]

# For a trivial demo candidate, take the *first sentence* of the article
# (THIS IS NOT A REAL SUMMARY—it's just a placeholder so you can
#  show BERTScore running; later you’ll replace with your model/system output.)
def first_sentence(text: str) -> str:
    # naive split on sentence terminators
    m = re.split(r"(?<=[.!?])\s+", text)
    return m[0] if m else text

candidates = [first_sentence(a) for a in articles]

# Preview a couple of before/after examples for your slide
print("\nSample (before/after cleaning & candidate/reference):\n")
for i in range(min(2, len(articles))):
    print(f"--- Example {i+1} ---")
    print("Article (first 220 chars):", articles[i][:220], "…")
    print("Candidate (first sentence):", candidates[i])
    print("Reference (highlights):", references[i])
    print()

# Compute BERTScore (English)
# Recommended default model is roberta-large; bert-score will auto-pick unless specified.
# On CPU and N small, this will finish quickly.
print("Computing BERTScore on", len(candidates), "pairs… (this may take a short while on CPU)")
P, R, F1 = bertscore(cands=candidates, refs=references, lang="en")

# Convert to Python floats and collect a DataFrame for saving
df = pd.DataFrame({
    "candidate": candidates,
    "reference": references,
    "P": [float(p) for p in P],
    "R": [float(r) for r in R],
    "F1": [float(f) for f in F1],
})

# Save results—use this CSV as evidence in your slides
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved BERTScore results to: {OUTPUT_CSV}")
print(df.head(3))

# Quick aggregate for narration
print("\nAggregate (mean over", len(df), "examples):")
print("P_mean =", df["P"].mean())
print("R_mean =", df["R"].mean())
print("F1_mean =", df["F1"].mean())
