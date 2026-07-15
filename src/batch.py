"""
Batch processing utilities.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tqdm import tqdm

from src.indexer import process_pdf
from src.models import ParserStatistics


def process_all(records):

    stats = ParserStatistics(total=len(records))

    log_dir = Path("output/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "process_log.csv"

    with open(log_file, "w", newline="", encoding="utf-8") as logfile:

        writer = csv.writer(logfile)

        writer.writerow(
            [
                "year",
                "district",
                "ac_no",
                "constituency",
                "parser",
                "status",
                "time_seconds",
                "reason",
            ]
        )
        logfile.flush()

        for record in tqdm(records):

            pdf = Path(record.output_path)

            excel = pdf.with_suffix(".xlsx")

            if excel.exists():

                stats.skipped += 1

                writer.writerow(
                    [
                        record.year,
                        record.district,
                        record.ac_no,
                        record.constituency,
                        "",
                        "SKIPPED",
                        "",
                        "Excel already exists",
                    ]
                )
                logfile.flush()

                continue

            result = process_pdf(pdf)

            if result.success:

                result.dataframe.to_excel(excel, index=False)

                stats.success += 1

                if result.parser == "camelot_lattice":
                    stats.camelot_lattice += 1

                writer.writerow(
                    [
                        record.year,
                        record.district,
                        record.ac_no,
                        record.constituency,
                        result.parser,
                        "SUCCESS",
                        round(result.processing_time, 2),
                        "",
                    ]
                )
                logfile.flush()

            else:

                stats.failed += 1

                writer.writerow(
                    [
                        record.year,
                        record.district,
                        record.ac_no,
                        record.constituency,
                        result.parser,
                        "FAILED",
                        round(result.processing_time, 2),
                        result.reason,
                    ]
                )
                logfile.flush()

    print()
    print("=" * 60)
    print("Batch Processing Summary")
    print("=" * 60)
    print(f"Total PDFs        : {stats.total}")
    print(f"Successful        : {stats.success}")
    print(f"Failed            : {stats.failed}")
    print(f"Skipped           : {stats.skipped}")
    print()
    print(f"Camelot Lattice   : {stats.camelot_lattice}")
    print()
    print(f"Process log saved : {log_file}")

    return stats
