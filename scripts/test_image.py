import fitz

pdf = fitz.open("output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf")

page = pdf[0]

pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))

pix.save("page1_600.png")

print("saved")
