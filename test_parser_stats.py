from src.parser import parse_pdf

pdf = "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"

metadata, df = parse_pdf(pdf)

print("Rows:", len(df))

print()

print("First polling station:", df.iloc[0, 0])

print("Last polling station:", df.iloc[-1, 0])

print()

print(df.tail(10))
