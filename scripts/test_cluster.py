import fitz
import cv2
import numpy as np


def pdf_page_to_image(pdf_path, page_no=0, dpi=600):
    """
    Render one PDF page as an OpenCV image.
    """

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


def detect_boxes(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    # Detect vertical lines

    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, 120),
    )

    vertical = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        vertical_kernel,
        iterations=2,
    )

    # Detect horizontal lines

    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (120, 1),
    )

    horizontal = cv2.morphologyEx(
        thresh,
        cv2.MORPH_OPEN,
        horizontal_kernel,
        iterations=2,
    )

    table = cv2.add(vertical, horizontal)

    contours, _ = cv2.findContours(
        table,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    boxes = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(contour)

        if w < 20 or h < 20:
            continue

        boxes.append((x, y, w, h))

    return boxes

def extract_vertical_lines(boxes):

    xs = []

    for x, y, w, h in boxes:

        xs.append(x)
        xs.append(x + w)

    xs = sorted(xs)

    merged = []

    THRESHOLD = 10

    for x in xs:

        if not merged:

            merged.append(x)

        elif abs(x - merged[-1]) < THRESHOLD:

            merged[-1] = int((merged[-1] + x) / 2)

        else:

            merged.append(x)

    return merged
    
def extract_horizontal_lines(boxes):

    ys = []

    for x, y, w, h in boxes:

        ys.append(y)
        ys.append(y + h)

    ys = sorted(ys)

    merged = []

    THRESHOLD = 10

    for y in ys:

        if not merged:

            merged.append(y)

        elif abs(y - merged[-1]) < THRESHOLD:

            merged[-1] = int((merged[-1] + y) / 2)

        else:

            merged.append(y)

    return merged

def draw_grid(image, vertical_lines, horizontal_lines):

    output = image.copy()

    # Draw vertical lines
    for x in vertical_lines:

        cv2.line(
            output,
            (x, 0),
            (x, image.shape[0]),
            (0, 255, 0),
            2,
        )

    # Draw horizontal lines
    for y in horizontal_lines:

        cv2.line(
            output,
            (0, y),
            (image.shape[1], y),
            (255, 0, 0),
            2,
        )

    return output

def merge_positions(values, tolerance=8):

    values = sorted(values)

    merged = []

    for v in values:

        if not merged:
            merged.append(v)

        elif abs(v - merged[-1]) <= tolerance:
            merged[-1] = int((merged[-1] + v) / 2)

        else:
            merged.append(v)

    return merged

def main():

    pdf = "output/2026/18_CUDDALORE/AC151_Tittakudi (SC).pdf"

    image = pdf_page_to_image(pdf)

    boxes = detect_boxes(image)
    
    # Collect all x positions

    x_positions = []

    for x, y, w, h in boxes:
        x_positions.append(x)
        x_positions.append(x + w)

    # Collect all y positions

    y_positions = []

    for x, y, w, h in boxes:
        y_positions.append(y)
        y_positions.append(y + h)

    print(f"\nBoxes detected : {len(boxes)}")

    vertical_lines = extract_vertical_lines(boxes)

    horizontal_lines = extract_horizontal_lines(boxes)

    print(f"\nVertical lines : {len(vertical_lines)}")
    print(f"Horizontal lines : {len(horizontal_lines)}")

    output = draw_grid(
        image,
        vertical_lines,
        horizontal_lines,
    )

    cv2.imwrite("grid_lines.png", output)

    print("\nSaved grid_lines.png")

    print("\nSaved boxes_numbered.png")


if __name__ == "__main__":
    main()
