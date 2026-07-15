from src.engines.camelot_lattice import parse_with_camelot_lattice

pdf = "output/2026/35_CHENGALPATTU/AC027_Shozhinganallur.pdf"

metadata, df = parse_with_camelot_lattice(pdf)

print("\nSHAPE")
print(df.shape)

print("\nROWS 0-8\n")

for i in range(9):

    print("=" * 80)
    print("ROW", i)
    print(df.iloc[i].tolist())
