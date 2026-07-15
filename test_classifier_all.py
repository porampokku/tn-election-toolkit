from pathlib import Path
from collections import Counter

from src.classifier import classify_pdf

counter = Counter()

for pdf in sorted(Path("output/2026").rglob("*.pdf")):

    kind = classify_pdf(pdf)

    counter[kind] += 1

    print(f"{kind:9} {pdf.name}")

print()
print("Summary")
print("-------")

for k, v in counter.items():
    print(f"{k:9}: {v}")
