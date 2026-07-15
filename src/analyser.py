"""
Analyse parser performance and generate diagnostic reports.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from src.classifier import classify_pdf
from src.indexer import process_pdf


def analyse(records, log_dir: str = "output/logs"):

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    success = []
    failed = []
    scanned = []

    success_csv = log_dir / "digital_success.csv"
    failed_csv = log_dir / "digital_failed.csv"
    scanned_csv = log_dir / "scanned.csv"

    with (
        open(success_csv, "w", newline="", encoding="utf-8") as success_file,
        open(failed_csv, "w", newline="", encoding="utf-8") as failed_file,
        open(scanned_csv, "w", newline="", encoding="utf-8") as scanned_file,
    ):

        success_writer = csv.writer(success_file)
        failed_writer = csv.writer(failed_file)
        scanned_writer = csv.writer(scanned_file)

        header = [
            "year",
            "district_no",
            "district",
            "ac_no",
            "constituency",
            "pdf_name",
            "reason",
        ]

        success_writer.writerow(header)
        failed_writer.writerow(header)
        scanned_writer.writerow(header)

        for record in tqdm(records):

            pdf = Path(record.output_path)

            pdf_type = classify_pdf(pdf)

            if pdf_type == "scanned":

                scanned.append(record)

                scanned_writer.writerow([
                    record.year,
                    record.district_no,
                    record.district,
                    record.ac_no,
                    record.constituency,
                    record.pdf_name,
                    "Scanned PDF",
                ])

                continue

            try:

                metadata, dataframe = process_pdf(pdf)

                if dataframe.empty:
                    raise RuntimeError("Empty dataframe")

                success.append(record)

                success_writer.writerow([
                    record.year,
                    record.district_no,
                    record.district,
                    record.ac_no,
                    record.constituency,
                    record.pdf_name,
                    "",
                ])

            except Exception as e:

                failed.append(record)

                failed_writer.writerow([
                    record.year,
                    record.district_no,
                    record.district,
                    record.ac_no,
                    record.constituency,
                    record.pdf_name,
                    str(e),
                ])

    print()
    print("Analysis complete")
    print("-----------------")
    print(f"Digital success : {len(success)}")
    print(f"Digital failed  : {len(failed)}")
    print(f"Scanned PDFs    : {len(scanned)}")

    print()
    print("Reports written to")
    print(success_csv)
    print(failed_csv)
    print(scanned_csv)

    return success, failed, scanned
