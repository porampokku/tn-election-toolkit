from pathlib import Path

import pandas as pd


rows = []

csvs = sorted(Path("output/2026").glob("*/*.csv"))

print(f"Checking {len(csvs)} CSV files")

for csv in csvs:

    try:

        df = pd.read_csv(csv)

        row = {
            "file": csv.name,
            "rows": len(df),
            "columns": len(df.columns),
            "polling_stations": (
                df["PS. No"].nunique()
                if "PS. No" in df.columns
                else None
            ),
            "duplicate_ps": (
                df["PS. No"].duplicated().sum()
                if "PS. No" in df.columns
                else None
            ),
            "status": "PASS",
            "reason": "",
        }

    except Exception as e:

        row = {
            "file": csv.name,
            "rows": None,
            "columns": None,
            "polling_stations": None,
            "duplicate_ps": None,
            "status": "FAIL",
            "reason": str(e),
        }

    rows.append(row)

report = pd.DataFrame(rows)

report.to_csv(
    "qa_report_2026.csv",
    index=False,
)

print(report["status"].value_counts())

print("\nReport written to qa_report_2026.csv")
