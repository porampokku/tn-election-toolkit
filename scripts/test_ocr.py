import fitz
import cv2
import pytesseract

PDF = "output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf"

# Render first page
doc = fitz.open(PDF)
page = doc.load_page(0)

pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))
pix.save("page1.png")

# Read image
img = cv2.imread("page1.png")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Binary threshold
_, thresh = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU,
)

cv2.imwrite("page1_bw.png", thresh)

# OCR
text = pytesseract.image_to_string(
    thresh,
    config="--oem 3 --psm 6"
)

with open("ocr_output.txt", "w", encoding="utf-8") as f:
    f.write(text)

print(text[:3000])
