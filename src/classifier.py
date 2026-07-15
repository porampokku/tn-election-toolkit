"""
Classify PDFs as digital, scanned or mixed.
"""

from pathlib import Path

import pdfplumber


def classify_pdf(pdf_path: str | Path) -> str:
    """
    Returns

        digital
        scanned
        mixed
    """

    pdf_path = Path(pdf_path)

    pages = 0
    text_pages = 0

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            pages += 1

            text = page.extract_text()

            if text and len(text.strip()) > 100:
                text_pages += 1

    if text_pages == 0:
        return "scanned"

    if text_pages == pages:
        return "digital"

    return "mixed"
