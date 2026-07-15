from src.engines.camelot_reverse import parse_with_camelot_reverse
from src.transformer import transform

pdf = "output/2026/35_CHENGALPATTU/AC027_Shozhinganallur.pdf"

metadata, df = parse_with_camelot_reverse(pdf)

print(metadata)

print(df.head())

print(df.columns)

clean = transform(df)

print()

print(clean.head())

print(clean.shape)
