from src.parser import parse_pdf

pdf = "output/2026/35_CHENGALPATTU/AC027_Shozhinganallur.pdf"

metadata, df = parse_pdf(pdf)

print("\nMETADATA\n")
print(metadata)

print("\nSHAPE\n")
print(df.shape)

print("\nCOLUMNS\n")
for i, col in enumerate(df.columns):
    print(i, repr(col))

print("\nFIRST 10 ROWS\n")
print(df.head(10))

print("\nFIRST COLUMN VALUES\n")
print(df.iloc[:20, 0])
print(df.iloc[2])
