from pathlib import Path

from src.parser import extract_rows
from src.parser import build_dataframe
from src.parser import save_excel

pdf = Path(
    "output/2026/01_TIRUVALLUR/AC001_Gummidipoondi.pdf"
)

rows = extract_rows(pdf)

df = build_dataframe(rows)

print(df.head())

save_excel(
    df,
    Path("output/data/AC001_clean.xlsx")
)

print(df.columns.tolist())
