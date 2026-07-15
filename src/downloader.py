"""
Download Form 20 PDFs.
"""

from __future__ import annotations

from pathlib import Path

import requests
from tqdm import tqdm

from src.config import USER_AGENT
from src.models import ElectionRecord
from src.utils import sanitise_filename


def make_output_path(record: ElectionRecord, root: Path) -> Path:
    """
    Create the destination filename.
    """

    district_folder = (
        root
        / str(record.year)
        / f"{record.district_no:02d}_{sanitise_filename(record.district)}"
    )

    district_folder.mkdir(parents=True, exist_ok=True)

    filename = (
        f"AC{record.ac_no:03d}_"
        f"{sanitise_filename(record.constituency)}.pdf"
    )

    return district_folder / filename


def download_record(record: ElectionRecord, root: Path) -> bool:

    output = make_output_path(record, root)

    record.output_path = output

    if output.exists():
        return True

    response = requests.get(
        record.pdf_url,
        headers={"User-Agent": USER_AGENT},
        timeout=120,
        stream=True,
    )

    if response.status_code != 200:
        return False

    with open(output, "wb") as f:

        for chunk in response.iter_content(1024 * 64):

            if chunk:
                f.write(chunk)

    return True


def download_all(records: list[ElectionRecord], output_dir: str = "output"):

    root = Path(output_dir)

    success = 0

    failed = 0

    for record in tqdm(records):

        ok = download_record(record, root)

        if ok:
            success += 1
        else:
            failed += 1
            print(f"Failed: {record.pdf_name}")

    print()
    print(f"Downloaded : {success}")
    print(f"Failed     : {failed}")
