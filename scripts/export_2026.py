from pathlib import Path

from src.parser import parse_pdf
from src.exporter import export_dataframe


pdfs = sorted(Path("output/2026").glob("*/*.pdf"))

print(f"Found {len(pdfs)} PDFs")

success = 0
failed = 0

for pdf in pdfs:

    print(f"Processing {pdf.name}")

    try:

        _, df = parse_pdf(pdf)

        print(pdf.name, df.shape)
        print(df.head(2))
        
        print("DataFrame shape:", df.shape)
        print(df.head())

        export_dataframe(
            df,
            pdf.with_suffix("")
        )

        success += 1

    except Exception as e:

        failed += 1
        print(f"FAILED: {pdf.name}")
        print(e)

print("\n" + "=" * 60)
print("Finished")
print(f"Successful : {success}")
print(f"Failed     : {failed}")
