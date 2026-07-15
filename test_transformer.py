from src.parser import parse_pdf
from src.transformer import transform

pdf = "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"

metadata, df = parse_pdf(pdf)

print("Raw shape")

print(df.shape)

print()

df = transform(df)

print("Clean shape")

print(df.shape)

print()

print(df.head())

print()

print(df.dtypes)

print()

print(metadata)
