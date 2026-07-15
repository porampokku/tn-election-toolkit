"""
Parser for Tamil Nadu Form 20 PDFs.
"""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber


def clean_cell(value):

    if value is None:
        return ""

    value = str(value)

    value = value.replace("\n", " ")

    value = " ".join(value.split())

    return value


def merge_header_rows(table):

    if len(table) < 2:
        return table

    row1 = table[0]
    row2 = table[1]

    headers = []

    width = max(len(row1), len(row2))

    for i in range(width):

        top = clean_cell(row1[i]) if i < len(row1) else ""
        bottom = clean_cell(row2[i]) if i < len(row2) else ""

        if top.startswith("No of Valid Votes Cast in favour of"):
            top = ""

        if top and bottom:
            headers.append(f"{top} {bottom}")

        elif top:
            headers.append(top)

        else:
            headers.append(bottom)

    return [headers] + table[2:]


def looks_like_reverse_layout(table):
    """
    Detect reverse-layout Form 20 PDFs.
    """

    if len(table) < 5:
        return False

    # Search the first few rows rather than only the first cell.
    for row in table[:5]:

        text = " ".join(
            clean_cell(x)
            for x in row
            if x
        ).upper()

        if "GENERAL ELECTIONS" in text:
            return True

    return False


def build_reverse_headers(table):
    """
    Build headers for reverse-layout PDFs.
    Candidate names are unavailable because the text is reversed,
    so temporary names are assigned.
    """

    row = table[2]

    n = len(row)

    headers = []

    for i in range(n):

        if i == 0:
            headers.append("Serial No. Of Polling Station")

        elif i == 1:
            headers.append("Polling Station")

        elif i == n - 5:
            headers.append("NOTA")

        elif i == n - 4:
            headers.append("Total of Valid Votes")

        elif i == n - 3:
            headers.append("No. Of Rejected Votes")

        elif i == n - 2:
            headers.append("Total")

        elif i == n - 1:
            headers.append("No. Of Tendered Votes")

        else:
            headers.append(f"Candidate_{i-1:02d}")

    return headers


def extract_metadata(first_page):

    text = first_page.extract_text() or ""

    metadata = {}

    ac = re.search(
        r"(\d+)\s*-\s*([A-Z0-9\-\(\)\. ]+?)\s+Assembly",
        text,
        re.I,
    )

    if ac:

        metadata["ac_no"] = int(ac.group(1))

        metadata["constituency"] = ac.group(2).strip()

    electors = re.search(
        r"Total No\.?\s*of Electors.*?(\d+)",
        text,
        re.I,
    )

    if electors:
        metadata["total_electors"] = int(electors.group(1))

    metadata["pages"] = len(first_page.pdf.pages)

    return metadata
def parse_with_camelot_lattice(pdf_path):
    """
    Parse one Form 20 PDF extracted using pdfplumber.
    Supports both the normal layout and the reverse-header layout.
    """

    rows = []
    headers = None

    with pdfplumber.open(pdf_path) as pdf:

        metadata = extract_metadata(pdf.pages[0])

        for page in pdf.pages:

            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                if not table:
                    continue

                # -----------------------------
                # Reverse-layout PDFs
                # -----------------------------
                if looks_like_reverse_layout(table):

                    headers_this_page = build_reverse_headers(table)

                    # Skip:
                    # row 0 -> title
                    # row 1 -> candidate names
                    # row 2 -> party names
                    # row 3 -> column numbers
                                        # Find the first real polling station row
                    start = 0

                    for i, row in enumerate(table):

                        first = clean_cell(row[0])

                        second = (
                            clean_cell(row[1])
                            if len(row) > 1
                            else ""
                        )

                        if first == "1" and second == "1":
                            start = i
                            break

                    data_rows = table[start:]

                # -----------------------------
                # Normal PDFs
                # -----------------------------
                else:

                    table = merge_header_rows(table)

                    headers_this_page = [
                        clean_cell(x)
                        for x in table[0]
                    ]

                    data_rows = table[1:]

                # -----------------------------
                # Save headers once
                # -----------------------------
                if headers is None:
                    headers = headers_this_page

                # -----------------------------
                # Store rows
                # -----------------------------
                for row in data_rows:

    row = [
        clean_cell(x)
        for x in row
    ]

    if len(row) != len(headers):
        continue

    if not any(row):
        continue

    first = row[0].strip()

    if first == "":
        continue

    # Skip repeated page headers
    if first in ("N .LS", ".O"):
        continue

    # Skip postal ballot summary
    if first.startswith("No. of votes"):
        continue

    if first.startswith("Postal"):
        continue

    # Skip totals
    if first.startswith("Total"):
        continue

    if first.startswith("Page"):
        continue

    # Only keep polling station rows
    if not first.isdigit():
        continue

    rows.append(row)

    df = pd.DataFrame(rows, columns=headers)

    return metadata, df
