from pathlib import Path

from src.parser import parse_pdf

pdf_dir = Path("output/2026")
pdf_files = sorted(pdf_dir.rglob("*.pdf"))

print(f"Found {len(pdf_files)} PDFs\n")

success = 0
failed = []

for pdf in pdf_files:

    try:
        metadata, df = parse_pdf(pdf)

        print(f"✓ {pdf.name} ({len(df)} polling stations)")

        success += 1

    except Exception as e:

        print(f"✗ {pdf.name}")

        failed.append((pdf.name, str(e)))

print("\n" + "=" * 60)

print(f"Successful : {success}")
print(f"Failed     : {len(failed)}")

if failed:
    print("\nFailures:")
    for name, err in failed:
        print(f"{name}: {err}")
