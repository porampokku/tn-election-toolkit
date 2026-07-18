import fitz
import os

PDF = "output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf"

doc = fitz.open(PDF)

os.makedirs("debug_ac151", exist_ok=True)

for i, page in enumerate(doc):

    pix = page.get_pixmap(matrix=fitz.Matrix(6, 6))

    outfile = f"debug_ac151/page_{i+1:02d}.png"

    pix.save(outfile)

    print(outfile)
