"""
Parser for reverse-layout Form 20 PDFs.
"""

from __future__ import annotations

import pdfplumber
import camelot
import pandas as pd


def parse_with_camelot_reverse(pdf_path):
    """
    Parse reverse-layout Form 20 PDFs.

    These PDFs contain four header rows before the actual polling
    station data.
    """

    # ----------------------------
    # Metadata
    # ----------------------------

    metadata = {}

    with pdfplumber.open(pdf_path) as pdf:

        metadata["pages"] = len(pdf.pages)

    # ----------------------------
    # Extract tables
    # ----------------------------

    tables = camelot.read_pdf(

        str(pdf_path),

        pages="all",

        flavor="lattice",

    )

    if len(tables) == 0:

        raise ValueError("No tables found.")

    dataframe = pd.concat(

        [table.df for table in tables],

        ignore_index=True,

    )

    # ----------------------------
    # Detect reverse layout
    # ----------------------------

    first = str(dataframe.iloc[0, 0])

    if "FORM 20" not in first:

        raise ValueError("Not a reverse-layout Form 20.")

    # ----------------------------
    # Remove header rows
    # ----------------------------

    dataframe = dataframe.iloc[4:].reset_index(drop=True)

    # ----------------------------
    # Rename columns
    # ----------------------------

    column_names = []

    for i in range(len(dataframe.columns)):

        if i == 0:

            column_names.append(
                "Serial No. Of Polling Station"
            )

        elif i == len(dataframe.columns) - 4:

            column_names.append(
                "Total of Valid Votes"
            )

        elif i == len(dataframe.columns) - 3:

            column_names.append(
                "No. Of Rejected Votes"
            )

        elif i == len(dataframe.columns) - 2:

            column_names.append(
                "Total"
            )

        elif i == len(dataframe.columns) - 1:

            column_names.append(
                "No. Of Tendered Votes"
            )

        elif i == len(dataframe.columns) - 5:

            column_names.append(
                "NOTA"
            )

        else:

            column_names.append(
                f"Candidate_{i:02d}"
            )

    dataframe.columns = column_names

    return metadata, dataframe
