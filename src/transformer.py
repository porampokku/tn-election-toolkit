"""
Transforms parsed Form 20 tables into a clean analysis-ready DataFrame.
"""

from __future__ import annotations

import pandas as pd


COLUMN_MAP = {

    # Standard headers
    "Serial No. Of Polling Station": "serial_no",
    "Serial No Of Polling Station": "serial_no",
    "Serial No. of Polling Station": "serial_no",
    "Table Serial No.": "serial_no",
    "Sl. No.": "serial_no",
    "Sl No.": "serial_no",

    "Polling Station": "polling_station",
    "Polling Station No": "polling_station",
    "Polling Station No.": "polling_station",
    "Polling Station Number": "polling_station",
    "PS No": "polling_station",
    "PS. No": "polling_station",

    "Total of Valid Votes": "total_valid_votes",
    "Total of valid votes": "total_valid_votes",
    "No. Of Rejected Votes": "rejected_votes",
    "No. of rejected votes": "rejected_votes",
    "No. Of Tendered Votes": "tendered_votes",
    "Total No. of tendere d votes": "tendered_votes",
    "NOTA": "nota",
    'Votes for "NOTA" option': "nota",
    "Total": "total_votes",
    
    # Short header variants
    "Polling": "polling_station",
    "Slno": "serial_no",
    "Sl No": "serial_no",
    "Sl. No": "serial_no",

    "Total of Valid": "total_valid_votes",
    "No. of Rejected": "rejected_votes",
    "No. of tendered": "tendered_votes",

    # Mirrored layouts
    ".oN laireS elbaT": "serial_no",
    "oN .SP": "polling_station",

    "setoV dilaV fO .oN": "total_valid_votes",
    "setoV detcejeR fo oN": "rejected_votes",
    "setoV deredneT fo oN": "tendered_votes",
    "ATON": "nota",
    "latoT": "total_votes",
}


def _normalise(text):

    text = str(text).strip()

    # Exact mapping
    if text in COLUMN_MAP:
        return COLUMN_MAP[text]

    # Mirrored text
    rev = text[::-1]

    if rev in COLUMN_MAP:
        return COLUMN_MAP[rev]

    low = text.lower()

    # Generic polling station headers
    if "polling" in low and "station" in low:

        if "serial" in low:
            return "serial_no"

        return "polling_station"

    # Generic vote columns
    if "valid" in low and "vote" in low:
        return "total_valid_votes"

    if "rejected" in low:
        return "rejected_votes"

    if "tender" in low:
        return "tendered_votes"

    if "nota" in low:
        return "nota"

    if low == "total":
        return "total_votes"

    return text


def transform(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    # ---------------------------------------------
    # Standardise column names
    # ---------------------------------------------

    df.columns = [_normalise(c) for c in df.columns]

    # ---------------------------------------------
    # Remove duplicate columns
    # ---------------------------------------------

    df = df.loc[:, ~df.columns.duplicated()]

    # ---------------------------------------------
    # Determine polling station column
    # ---------------------------------------------

    if "polling_station" in df.columns:

        polling_column = "polling_station"

    elif "serial_no" in df.columns:

        polling_column = "serial_no"

    else:

        polling_column = None

        for col in df.columns:

            name = str(col).lower()

            if "polling" in name and "station" in name:
                polling_column = col
                break

            if (
                "serial" in name
                and "polling" in name
                and "station" in name
            ):
                polling_column = col
                break

        if polling_column is None:
            raise KeyError("Polling station column not found")

    if polling_column != "polling_station":

        df = df.rename(
            columns={
                polling_column: "polling_station"
            }
        )

    # ---------------------------------------------
    # Remove empty rows
    # ---------------------------------------------

    df = df.dropna(how="all")

    # ---------------------------------------------
    # Convert polling station numbers
    # ---------------------------------------------

    df["polling_station"] = pd.to_numeric(
        df["polling_station"],
        errors="coerce",
    )

    df = df[df["polling_station"].notna()]

    df["polling_station"] = (
        df["polling_station"]
        .astype(int)
    )

    # ---------------------------------------------
    # Convert remaining numeric columns
    # ---------------------------------------------

    for col in df.columns:

        if col == "polling_station":
            continue

        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            pass

    # ---------------------------------------------
    # Remove duplicate polling stations
    # ---------------------------------------------

    df = df.drop_duplicates(
        subset="polling_station"
    )

    # ---------------------------------------------
    # Sort
    # ---------------------------------------------

    df = df.sort_values("polling_station")

    df = df.reset_index(drop=True)

    return df
