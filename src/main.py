"""
Main entry point for the Tamil Nadu Election Toolkit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.scraper import discover_year
from src.downloader import download_all
from src.batch import process_all
from src.index import build_index


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Tamil Nadu Election Toolkit"
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Election year (2006, 2011, 2016, 2021, 2026)"
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="Download Form 20 PDFs"
    )

    parser.add_argument(
        "--excel",
        action="store_true",
        help="Generate Excel files"
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    print()
    print(f"Discovering constituencies for {args.year}...")

    records = discover_year(args.year)

    print(f"Found {len(records)} constituencies.")

    #
    # Download PDFs
    #
    if args.download:

        print()
        print("Downloading PDFs...")
        print()

        download_all(records)

    #
    # If user skipped download, reconstruct expected PDF paths
    #
    else:

        root = Path("output")

        for record in records:

            district_folder = (
                root
                / str(record.year)
                / f"{record.district_no:02d}_{record.district.replace('/', '_')}"
            )

            record.output_path = (
                district_folder
                / f"AC{record.ac_no:03d}_{record.constituency.replace('/', '_')}.pdf"
            )

    #
    # Generate Excel files
    #
    if args.excel:

        print()
        print("Creating Excel files...")
        print()

        process_all(records)

    #
    # Build master index
    #
    index = build_index(records)

    output_dir = Path("output/data")

    output_dir.mkdir(parents=True, exist_ok=True)

    index_file = output_dir / f"index_{args.year}.csv"

    index.to_csv(index_file, index=False)

    print()
    print(f"Index written to: {index_file}")

    print()
    print("Finished.")


if __name__ == "__main__":
    main()
