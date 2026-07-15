"""
Parser for Tamil Nadu Form 20 PDFs.

Supports both:
    • Standard Form 20 layout
    • Reverse-header Form 20 layout

Output:
    metadata, pandas.DataFrame
"""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def clean_cell(value):
    """Normalise one table cell."""

    if value is None:
        return ""

    value = str(value)

    value = value.replace("\n", " ")

    value = " ".join(value.split())

    return value


# ---------------------------------------------------------------------
# Header handling for normal PDFs
# ---------------------------------------------------------------------

def merge_header_rows(table):
    """
    Merge the first two header rows of the normal Form 20 layout.
    """

    if len(table) < 2:
        return table

    row1 = table[0]
    row2 = table[1]

    width = max(len(row1), len(row2))

    headers = []

    for i in range(width):

        top = clean_cell(row1[i]) if i < len(row1) else ""
        bottom = clean_cell(row2[i]) if i < len(row2) else ""

        if top.startswith("No of Valid Votes"):
            top = ""

        if top and bottom:
            headers.append(f"{top} {bottom}".strip())

        elif top:
            headers.append(top)

        else:
            headers.append(bottom)

    return [headers] + table[2:]


# ---------------------------------------------------------------------
# Detect reverse-layout PDFs
# ---------------------------------------------------------------------

def looks_like_reverse_layout(table):
    """
    Reverse-layout PDFs always start with:

        FORM 20 - FINAL RESULT SHEET...

    in the first cell.
    """

    if not table:
        return False

    first = clean_cell(table[0][0]).upper()

    return first.startswith("FORM 20")


# ---------------------------------------------------------------------
# Build headers for reverse PDFs
# ---------------------------------------------------------------------

def build_reverse_headers(table):

    n = len(table[0])

    headers = []

    for i in range(n):

        if i == 0:

            headers.append(
                "Serial No. Of Polling Station"
            )

        elif i == 1:

            headers.append(
                "Polling Station"
            )

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

            headers.append(
                f"Candidate_{i-1:02d}"
            )

    return headers


# ---------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------

def extract_metadata(first_page):

    text = first_page.extract_text() or ""

    metadata = {}

    ac = re.search(
        r"(\d+)\s*[-–]\s*([A-Z0-9(). /\-]+?)\s+Assembly",
        text,
        flags=re.I,
    )

    if ac:

        metadata["ac_no"] = int(ac.group(1))

        metadata["constituency"] = ac.group(2).strip()

    electors = re.search(
        r"Total\s+No\.?\s+of\s+Electors.*?(\d+)",
        text,
        flags=re.I,
    )

    if electors:

        metadata["total_electors"] = int(
            electors.group(1)
        )

    metadata["pages"] = len(first_page.pdf.pages)

    return metadata
    
def looks_like_2026_roundwise(table):
    """
    Detect 2026 Round Wise Abstract pages,
    including continuation pages.
    """

    if not table:
        return False

    first = clean_cell(table[0][0]).upper()

    header = " ".join(
        clean_cell(c)
        for c in table[0]
        if c
    ).upper()

    print("=" * 70)
    print("FIRST:")
    print(first)
    print()
    print("HEADER:")
    print(header)
    print("=" * 70)

    # First page
    if (
        "FORM - 20" in first
        and "ROUND WISE ABSTRACT" in first
    ):
        return True

    # Continuation pages
    if header.startswith(".ON LAIRES ELBAT"):
        return True

    return False
def parse_2026_roundwise(table):
    """
    Parse one 2026 Round Wise Abstract table.

    Returns
    -------
    headers_this_page, data_rows
    """

    # First page
    if "FORM - 20" in clean_cell(table[0][0]).upper():

        header_row = 2
        party_row = 3
        first_data = 4

    # Continuation pages
    else:

        header_row = 0
        party_row = 1
        first_data = 2

    headers = [
        clean_cell(x)
        for x in table[header_row]
    ]

    parties = [
        clean_cell(x)
        for x in table[party_row]
    ]

    merged = []

    for h, p in zip(headers, parties):

        if p:
            merged.append(f"{h} ({p})")
        else:
            merged.append(h)
            
    # Give meaningful names to the first two columns
    merged[0] = "Table Serial No."
    merged[1] = "PS. No"

    return merged, table[first_data:]

    # ---------------------------------------------------------------------
    # Main parser
    # ---------------------------------------------------------------------

def parse_with_camelot_lattice(pdf_path):
    """
    Parse one Tamil Nadu Form 20 PDF.
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

                # --------------------------------------------------
                # Reverse-layout Form 20
                # --------------------------------------------------

                if looks_like_reverse_layout(table):

                    headers_this_page = build_reverse_headers(table)

                    # Locate the first real polling station row.
                    # It is the first row where both serial number
                    # and polling station equal "1".

                    start = None

                    for i, row in enumerate(table):

                        if len(row) < 2:
                            continue

                        first = clean_cell(row[0])

                        second = clean_cell(row[1])

                        if first == "1" and second == "1":
                            start = i
                            break

                    if start is None:
                        continue

                    data_rows = table[start:]

                # --------------------------------------------------
                # 2026 Round Wise Abstract
                # --------------------------------------------------

                elif looks_like_2026_roundwise(table):

                    headers_this_page, data_rows = parse_2026_roundwise(table)

                # --------------------------------------------------
                # Normal Form 20
                # --------------------------------------------------

                else:

                    table = merge_header_rows(table)

                    headers_this_page = [
                        clean_cell(x)
                        for x in table[0]
                    ]

                    data_rows = table[1:]

                # --------------------------------------------------
                # Save headers once
                # --------------------------------------------------

                if headers is None:
                    headers = headers_this_page

                # --------------------------------------------------
                # Process rows
                # --------------------------------------------------

                count = 0

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

                    # repeated page headers
                    if first in (
                        ".O",
                        "N .LS",
                    ):
                        continue

                    # page footer
                    if first.startswith("Page"):
                        continue

                    # totals
                    if first.startswith("Total"):
                        continue

                    # postal ballot summary
                    if first.startswith(
                        "No. of votes recorded"
                    ):
                        continue

                    if first.startswith("Postal"):
                        continue

                    rows.append(row)
                    count += 1
                    
                print("Rows added from this table:", count)
    # --------------------------------------------------
    # Build dataframe
    # --------------------------------------------------

    if headers is None:
        return metadata, pd.DataFrame()

    df = pd.DataFrame(rows, columns=headers)
    print("After DataFrame:", df.shape)

    # --------------------------------------------------
    # Remove duplicate column names produced by Camelot
    # --------------------------------------------------

    df = df.loc[:, ~df.columns.duplicated()]
    print("After duplicate columns:", df.shape)
    
    # --------------------------------------------------
    # Remove numbering row (1,2,3,4,...)
    # --------------------------------------------------

    if not df.empty:

        first = df.iloc[0].astype(str).tolist()

        expected = [str(i) for i in range(1, len(first) + 1)]

        if first == expected:

            df = df.iloc[1:].reset_index(drop=True)
            print("After numbering-row removal:", df.shape)

    # --------------------------------------------------
    # Fix mirrored headers found in some 2026 PDFs
    # --------------------------------------------------

    def _fix_header(text):

        text = str(text).strip()

        reversed_text = text[::-1]
        reversed_lower = reversed_text.lower()

        keywords = (
            "polling",
            "station",
            "serial",
            "table",
            "total",
            "valid",
            "votes",
            "nota",
            "rejected",
            "tendered",
            "ps",
        )

        if any(word in reversed_lower for word in keywords):
            return reversed_text

        return text

    df.columns = [_fix_header(col) for col in df.columns]

    # --------------------------------------------------
    # Remove repeated page headers that slipped through
    # --------------------------------------------------

    first_col = df.columns[0]

    df = df[
        ~df[first_col].astype(str).isin(
            [
                ".O",
                "N .LS",
                "SL. NO.",
                "Serial No.",
                "Table Serial No.",
            ]
        )
    ]
    print("After repeated-header removal:", df.shape)
    
    # --------------------------------------------------
    # Remove postal ballot summary rows
    # --------------------------------------------------

    df = df[
        ~df[first_col]
        .astype(str)
        .str.startswith(
            (
                "No. of votes",
                "Postal",
                "TOTAL",
                "Total",
            )
        )
    ]
    
    print("After postal removal:", df.shape)
    
    # --------------------------------------------------
    # Show rows that will be removed by numeric filter
    # --------------------------------------------------
    print("\nRows that will be removed by numeric filter:")
    bad = df[
        ~df[first_col]
          .astype(str)
          .str.fullmatch(r"\d+")
          .fillna(False)
    ]
    print(bad)


    # --------------------------------------------------
    # Keep only polling-station rows
    # --------------------------------------------------

    df = df[
        df[first_col]
        .astype(str)
        .str.fullmatch(r"\d+")
    ]
    print("After numeric filter:", df.shape)

    # --------------------------------------------------
    # Remove duplicate polling stations
    # --------------------------------------------------

    if "PS. No" in df.columns:

        df = df.drop_duplicates(
            subset=["PS. No"],
            keep="first",
        )

    else:

        df = df.drop_duplicates(
            subset=[first_col],
            keep="first",
        )
    
    print("After drop_duplicates:", df.shape)

    # --------------------------------------------------
    # Reset index
    # --------------------------------------------------

    # --------------------------------------------------
    # 2026 Round Wise PDFs:
    # Table Serial No. is only the page-wise table index.
    # Drop it if PS. No exists.
    # --------------------------------------------------

    if (
        "Table Serial No." in df.columns
        and "PS. No" in df.columns
    ):
        df = df.drop(columns=["Table Serial No."])
    
    df = df.reset_index(drop=True)

    return metadata, df
