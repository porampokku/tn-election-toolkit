"""
Create a master CSV index.
"""

import pandas as pd


def build_index(records):

    rows = []

    for record in records:

        rows.append({

            "year": record.year,
            "district_no": record.district_no,
            "district": record.district,
            "ac_no": record.ac_no,
            "constituency": record.constituency,
            "pdf": str(record.output_path),
            "excel": str(record.output_path).replace(".pdf", ".xlsx")

        })

    df = pd.DataFrame(rows)

    return df
