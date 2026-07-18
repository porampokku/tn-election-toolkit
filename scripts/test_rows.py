import fitz
import cv2
import numpy as np


PDF = "output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf"


# --------------------------------------------------------
# PDF -> image
# --------------------------------------------------------

doc = fitz.open(PDF)
page = doc[0]

pix = page.get_pixmap(dpi=600)

img = np.frombuffer(
    pix.samples,
    dtype=np.uint8,
).reshape(pix.height, pix.width, pix.n)

if pix.n == 4:
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
else:
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

_, thresh = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
)

# --------------------------------------------------------
# Horizontal lines
# --------------------------------------------------------

kernel = cv2.getStructuringElement(
    cv2.MORPH_RECT,
    (250, 1),
)

horizontal = cv2.morphologyEx(
    thresh,
    cv2.MORPH_OPEN,
    kernel,
    iterations=2,
)

# --------------------------------------------------------
# Find horizontal contours
# --------------------------------------------------------

contours, _ = cv2.findContours(
    horizontal,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

ys = []

for c in contours:

    x, y, w, h = cv2.boundingRect(c)

    if w < 1000:
        continue

    ys.append(y)

ys = sorted(ys)

# --------------------------------------------------------
# Merge nearby y positions
# --------------------------------------------------------

merged = []

for y in ys:

    if not merged:

        merged.append(y)

    elif y - merged[-1] < 10:

        merged[-1] = (merged[-1] + y) // 2

    else:

        merged.append(y)

print()

print("Horizontal lines:", len(merged))

print(merged)

# --------------------------------------------------------
# Draw
# --------------------------------------------------------

out = img.copy()

for y in merged:

    cv2.line(
        out,
        (0, y),
        (out.shape[1], y),
        (0, 0, 255),
        3,
    )

cv2.imwrite("rows.png", out)

print()

print("Saved rows.png")
