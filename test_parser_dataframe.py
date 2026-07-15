from src.parser import parse_pdf

pdf = "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"

metadata, df = parse_pdf(pdf)

print("METADATA")
print(metadata)

print()

print(df.head())

print()

print(df.shape)
