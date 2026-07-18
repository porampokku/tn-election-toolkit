import pytesseract
from PIL import Image

img = Image.open("page1_600.png")

text = pytesseract.image_to_string(img)

print(text[:5000])
