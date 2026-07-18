import fitz
import cv2
import numpy as np
import pytesseract


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

def deskew_image(image):
    """
    Detect page skew and rotate the page so that the table is horizontal.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    lines = cv2.HoughLinesP(
        thresh,
        rho=1,
        theta=np.pi / 180,
        threshold=300,
        minLineLength=800,
        maxLineGap=20,
    )

    if lines is None:
        print("No skew detected.")
        return image

    angles = []

    for line in lines:

        line = line.flatten()

        if len(line) != 4:
            continue

        x1, y1, x2, y2 = line

        angle = np.degrees(
            np.arctan2(
                y2 - y1,
                x2 - x1,
            )
        )

        if abs(angle) < 10:
            angles.append(angle)

    if len(angles) == 0:
        print("No usable skew angle.")
        return image

    skew_angle = np.median(angles)

    print(f"Detected skew angle: {skew_angle:.3f}°")

    h, w = image.shape[:2]

    matrix = cv2.getRotationMatrix2D(
        (w / 2, h / 2),
        skew_angle,
        1.0,
    )

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return rotated
    
def prepare_ocr_image(image):
    """
    Prepare an image for OCR while preserving thin digits.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0,
    )

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15,
    )

    return binary

def detect_boxes(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

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

    xs.sort()

    merged = []

    THRESHOLD = 10

    for x in xs:

        if not merged:

            merged.append(x)

        elif abs(x - merged[-1]) <= THRESHOLD:

            merged[-1] = int((merged[-1] + x) / 2)

        else:

            merged.append(x)

    return merged


def extract_horizontal_lines(boxes):

    ys = []

    for x, y, w, h in boxes:

        ys.append(y)
        ys.append(y + h)

    ys.sort()

    merged = []

    THRESHOLD = 10

    for y in ys:

        if not merged:

            merged.append(y)

        elif abs(y - merged[-1]) <= THRESHOLD:

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

    # Draw intersections

    for x in vertical_lines:
        for y in horizontal_lines:

            cv2.circle(
                output,
                (x, y),
                5,
                (0, 0, 255),
                -1,
            )

    return output
    
def build_form20_layout(vertical_lines, horizontal_lines):

    layout = {}

    # ---------------------------------------------------
    # Full-width headers
    # ---------------------------------------------------

    layout["title"] = (
        vertical_lines[0],
        horizontal_lines[0],
        vertical_lines[-1],
        horizontal_lines[1],
    )

    layout["election"] = (
        vertical_lines[0],
        horizontal_lines[1],
        vertical_lines[-1],
        horizontal_lines[2],
    )

    layout["constituency"] = (
        vertical_lines[0],
        horizontal_lines[2],
        vertical_lines[-1],
        horizontal_lines[3],
    )

    layout["valid_votes_title"] = (
        vertical_lines[3],
        horizontal_lines[3],
        vertical_lines[-5],
        horizontal_lines[4],
    )

    # ---------------------------------------------------
    # Party row
    # ---------------------------------------------------

    layout["party"] = []

    for c in range(3, len(vertical_lines) - 5):

        layout["party"].append(
            (
                c,
                vertical_lines[c],
                horizontal_lines[4],
                vertical_lines[c + 1],
                horizontal_lines[5],
            )
        )

    # ---------------------------------------------------
    # Candidate row
    # ---------------------------------------------------

    layout["candidate"] = []

    for c in range(3, len(vertical_lines) - 5):

        layout["candidate"].append(
            (
                c,
                vertical_lines[c],
                horizontal_lines[5],
                vertical_lines[c + 1],
                horizontal_lines[6],
            )
        )

    # ---------------------------------------------------
    # Column numbers
    # ---------------------------------------------------

    layout["column_numbers"] = []

    for c in range(len(vertical_lines) - 1):

        layout["column_numbers"].append(
            (
                c,
                vertical_lines[c],
                horizontal_lines[6],
                vertical_lines[c + 1],
                horizontal_lines[7],
            )
        )

    # ---------------------------------------------------
    # Data rows
    # ---------------------------------------------------

    layout["data"] = []

    for r in range(7, len(horizontal_lines) - 1):

        row = []

        for c in range(len(vertical_lines) - 1):

            row.append(
                (
                    c,
                    vertical_lines[c],
                    horizontal_lines[r],
                    vertical_lines[c + 1],
                    horizontal_lines[r + 1],
                )
            )

        layout["data"].append(row)

    return layout
    
def crop_cell(image, x1, y1, x2, y2):
    """
    Crop a cell while removing table borders.
    """

    LEFT = 8
    RIGHT = 8
    TOP = 4
    BOTTOM = 4

    return image[
        y1 + TOP : y2 - BOTTOM,
        x1 + LEFT : x2 - RIGHT,
    ]
    
def ocr_cell(image, x1, y1, x2, y2):
    """
    Crop one cell and prepare it for OCR.
    """

    cell = crop_cell(
        image,
        x1,
        y1,
        x2,
        y2,
    )

    if cell.size == 0:
        return None

    gray = cv2.cvtColor(
        cell,
        cv2.COLOR_BGR2GRAY,
    )

    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC,
    )

    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )[1]

    return processed
    
def ocr_number(image, x1, y1, x2, y2):

    processed = ocr_cell(
        image,
        x1,
        y1,
        x2,
        y2,
    )

    cv2.imwrite(
        "debug_number.png",
        processed,
    )

    print(processed.shape)
    print(processed.dtype)
    print(np.unique(processed))

    text = pytesseract.image_to_string(
        processed,
        config=(
            "--oem 3 "
            "--psm 7 "
            "-c tessedit_char_whitelist=0123456789"
        ),
    )

    print(repr(text))

    return text.strip()


def ocr_text(image, x1, y1, x2, y2):

    processed = ocr_cell(
        image,
        x1,
        y1,
        x2,
        y2,
    )

    return pytesseract.image_to_string(
        processed,
        config="--psm 7",
    ).strip()


def ocr_vertical_text(image, x1, y1, x2, y2):

    # Crop inside the cell
    cell = image[
        y1 + 5 : y2 - 5,
        x1 + 5 : x2 - 5,
    ]

    # Rotate vertical text to horizontal
    cell = cv2.rotate(
        cell,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    )

    # Remove remaining borders
    H, W = cell.shape[:2]

    cell = cell[
        2:H - 2,
        8:W - 8,
    ]

    # Convert to grayscale
    gray = cv2.cvtColor(
        cell,
        cv2.COLOR_BGR2GRAY,
    )

    # Enlarge
    gray = cv2.resize(
        gray,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC,
    )

    # Adaptive threshold
    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15,
    )

    # Slightly thicken characters
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (2, 2),
    )

    processed = cv2.dilate(
        processed,
        kernel,
        iterations=1,
    )

    cv2.imwrite(
        "debug_rotated.png",
        cell,
    )

    cv2.imwrite(
        "debug_processed.png",
        processed,
    )

    return pytesseract.image_to_string(
        processed,
        config=(
            "--oem 3 "
            "--psm 5 "
            "-c preserve_interword_spaces=1"
        ),
    ).strip()

def main():

    pdf = "output/2026/18_CUDDALORE/AC154_Panruti.pdf"

    image = pdf_page_to_image(
        pdf,
    )
    
    image = deskew_image(image)
    
    cv2.imwrite("deskewed.png", image)

    print("Saved deskewed.png")

    boxes = detect_boxes(image)

    print(f"\nBoxes detected : {len(boxes)}")

    vertical_lines = extract_vertical_lines(boxes)

    horizontal_lines = extract_horizontal_lines(boxes)

    print(f"Vertical lines : {len(vertical_lines)}")
    print(f"Horizontal lines : {len(horizontal_lines)}")
    
    print()

    print("Horizontal lines")

    for i, y in enumerate(horizontal_lines):
        print(i, y)

    print()

    preview_debug = image.copy()

    for i, y in enumerate(horizontal_lines):

        cv2.line(
            preview_debug,
            (0, y),
            (image.shape[1], y),
            (0, 0, 255),
            2,
        )

        cv2.putText(
            preview_debug,
            str(i),
            (20, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 0, 0),
            2,
        )

    cv2.imwrite(
        "horizontal_debug.png",
        preview_debug,
    )

    print()

    for i, y in enumerate(horizontal_lines):
        print(i, y)

    output = draw_grid(
        image,
        vertical_lines,
        horizontal_lines,
    )

    cv2.imwrite(
        "grid_lines.png",
        output,
    )
    layout = build_form20_layout(
        vertical_lines,
        horizontal_lines,
    )
    
    print("\nCandidate cells")

    for i, cell in enumerate(layout["candidate"]):
        print(i, cell)
    
    preview = image.copy()

    # --------------------------------------------------
    # Draw merged header cells
    # --------------------------------------------------

    header_names = [
        "title",
        "election",
        "constituency",
        "valid_votes_title",
    ]

    for name in header_names:

        x1, y1, x2, y2 = layout[name]

        cv2.rectangle(
            preview,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2,
        )

    # --------------------------------------------------
    # Party row
    # --------------------------------------------------

    for c, x1, y1, x2, y2 in layout["party"]:

        cv2.rectangle(
            preview,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            1,
        )

    # --------------------------------------------------
    # Candidate row
    # --------------------------------------------------

    for c, x1, y1, x2, y2 in layout["candidate"]:

        cv2.rectangle(
            preview,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            1,
        )

    # --------------------------------------------------
    # Column numbers
    # --------------------------------------------------

    for c, x1, y1, x2, y2 in layout["column_numbers"]:

        cv2.rectangle(
            preview,
            (x1, y1),
            (x2, y2),
            (255, 255, 0),
            1,
        )

    # --------------------------------------------------
    # Data cells
    # --------------------------------------------------

    for row in layout["data"]:

        for c, x1, y1, x2, y2 in row:

            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                1,
            )

    cv2.imwrite(
        "cells_preview.png",
        preview,
    )

    print("Saved cells_preview.png")
    # ---------------------------------------
    # OCR preprocessing test
    # ---------------------------------------

    print()

    print("Polling Station")
    print(
        ocr_number(
            image,
            *layout["data"][0][1][1:]
        )
    )

    print()

    print("Total Electors")
    print(
        ocr_number(
            image,
            *layout["data"][0][2][1:]
        )
    )

    print()

    print("Candidate Vote")
    print(
        ocr_number(
            image,
            *layout["data"][0][3][1:]
        )
    )

    print()

    cell = layout["candidate"][0]

    print(cell)

    _, x1, y1, x2, y2 = cell

    print("x1 =", x1)
    print("y1 =", y1)
    print("x2 =", x2)
    print("y2 =", y2)

    candidate = image[y1:y2, x1:x2]

    print(candidate.shape)

    cv2.imwrite(
        "candidate_before_rotation.png",
        candidate,
    )

    candidate = cv2.rotate(
        candidate,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    )

    cv2.imwrite(
        "candidate_after_rotation.png",
        candidate,
    )

    print("Saved candidate_raw.png")

    print()

    print("Party")
    print(
        ocr_vertical_text(
            image,
            *layout["party"][0][1:]
        )
    )

    print("Saved ocr_test.png")


if __name__ == "__main__":
    main()
