"""
Scraper for Tamil Nadu Assembly election Form 20 pages.
"""

from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.config import USER_AGENT, ASSEMBLY_PAGES
from src.models import ElectionRecord


def fetch_html(url: str) -> BeautifulSoup:
    """Download a webpage and return a BeautifulSoup object."""

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )

    response.raise_for_status()

    return BeautifulSoup(response.text, "lxml")


def discover_year(year: int) -> list[ElectionRecord]:
    """
    Discover all Form 20 PDFs for a given Assembly election year.
    """

    if year not in ASSEMBLY_PAGES:
        raise ValueError(f"No Assembly page configured for {year}")

    # Convert:
    # TNLA2026.aspx -> Form20_TNLA2026.aspx
    # TNLA2021.aspx -> Form20_TNLA2021.aspx
    # TNLA2016.aspx -> Form20_TNLA2016.aspx
    # AssemblyElections2011.aspx -> Form20_AssemblyElections2011.aspx
    # General_Elections_2006.aspx -> Form20_General_Elections_2006.aspx

    page = ASSEMBLY_PAGES[year]

    filename = page.split("/")[-1]

    page = page.replace(filename, "Form20_" + filename)

    soup = fetch_html(page)

    table = soup.find("table")

    if table is None:
        raise RuntimeError("Unable to locate Form 20 table.")

    records = []

    district_no = None
    district_name = None

    for row in table.find_all("tr"):

        cells = row.find_all("td")

        if not cells:
            continue

        # First constituency row of a district
        if len(cells) == 3:

            district_no = int(cells[0].get_text(strip=True))
            district_name = cells[1].get_text(strip=True)

            ac_cell = cells[2]

        # Remaining constituencies
        elif len(cells) == 1:

            if district_no is None:
                continue

            ac_cell = cells[0]

        else:
            continue

        link = ac_cell.find("a")

        if link is None:
            continue

        href = link.get("href")

        if not href or ".pdf" not in href.lower():
            continue

        pdf_url = urljoin(page, href)

        pdf_name = pdf_url.split("/")[-1]

        title = link.get("title", "").strip()

        match = re.match(r"(\d+)\.\s*(.*)", title)

        if match:
            ac_no = int(match.group(1))
            constituency = match.group(2).strip()
        else:
            ac_match = re.search(r"AC(\d+)", pdf_name, re.I)

            if not ac_match:
                continue

            ac_no = int(ac_match.group(1))
            constituency = title or "Unknown"

        records.append(
            ElectionRecord(
                year=year,
                district_no=district_no,
                district=district_name,
                ac_no=ac_no,
                constituency=constituency,
                pdf_name=pdf_name,
                pdf_url=pdf_url,
            )
        )

    records.sort(key=lambda x: x.ac_no)

    return records
