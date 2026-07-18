from pathlib import Path

from src.parser import parse_pdf


pdfs = sorted(Path("output/2026").rglob("*.pdf"))

print(f"Found {len(pdfs)} PDFs\n")

passed = 0
failed = 0

for pdf in pdfs:

    try:

        _, df = parse_pdf(pdf)

        cols = list(df.columns)

        valid_col = next(c for c in cols if "valid" in c.lower())

        rejected_col = next(c for c in cols if "rejected" in c.lower())

        tendered_col = next(c for c in cols if "tender" in c.lower())

        nota_col = next(c for c in cols if "nota" in c.lower())

        total_col = "Total"

        candidate_cols = cols[1:cols.index(valid_col)]

        candidate_total = (
            df[candidate_cols]
            .astype(int)
            .sum()
            .sum()
        )

        nota = df[nota_col].astype(int).sum()

        valid = df[valid_col].astype(int).sum()

        rejected = df[rejected_col].astype(int).sum()

        total = df[total_col].astype(int).sum()

        ps = len(df)

        ok = True

        if candidate_total + nota != valid:
            ok = False

        if valid + rejected != total:
            ok = False

        if ps != df["PS. No"].astype(int).max():
            ok = False

        if ok:
            print(f"✓ {pdf.stem}")
            passed += 1
        else:
            print(f"✗ {pdf.stem}")
            failed += 1

    except Exception as e:
        print(f"ERROR {pdf.stem}: {e}")
        failed += 1

print("\n==============================")
print("Passed:", passed)
print("Failed:", failed)
