import fitz
import cv2
import numpy as np


def pdf_page_to_image(pdf_path, page_no=0, dpi=600):

    doc = fitz.open(pdf_path)

    page = doc[page_no]

    pix = page.get_pixmap(dpi=dpi)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


pdf = "output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf"

image = pdf_page_to_image(pdf)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, thresh = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
)

# -------------------------
# Horizontal lines
# -------------------------

horizontal_kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (150, 1),
)

horizontal = cv2.morphologyEx(
    thresh,
    cv2.MORPH_OPEN,
    horizontal_kernel,
    iterations=2,
)

# -------------------------
# Vertical lines
# -------------------------

vertical_kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (1, 150),
)

vertical = cv2.morphologyEx(
    thresh,
    cv2.MORPH_OPEN,
    vertical_kernel,
    iterations=2,
)

output = image.copy()

# -------------------------
# Draw horizontal lines
# -------------------------

contours, _ = cv2.findContours(
    horizontal,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

print("Horizontal lines:", len(contours))

for c in contours:

    x, y, w, h = cv2.boundingRect(c)

    if w < 100:
        continue

    cv2.line(
        output,
        (x, y + h // 2),
        (x + w, y + h // 2),
        (255, 0, 0),
        2,
    )

# -------------------------
# Draw vertical lines
# -------------------------

contours, _ = cv2.findContours(
    vertical,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

print("Vertical lines:", len(contours))

for c in contours:

    x, y, w, h = cv2.boundingRect(c)

    if h < 100:
        continue

    cv2.line(
        output,
        (x + w // 2, y),
        (x + w // 2, y + h),
        (0, 255, 0),
        2,
    )

cv2.imwrite("grid_lines.png", output)

print("Saved grid_lines.png")
