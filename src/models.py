"""
Data models used throughout the toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------

@dataclass
class ElectionRecord:
    """
    Represents one Assembly Constituency Form 20 PDF.
    """

    year: int

    district_no: int

    district: str

    ac_no: int

    constituency: str

    pdf_name: str

    pdf_url: str

    output_path: Path | None = None

    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------
# Parser result
# ---------------------------------------------------------------------

@dataclass
class ProcessResult:
    """
    Result returned after processing one PDF.
    """

    success: bool

    parser: str

    metadata: dict = field(default_factory=dict)

    dataframe: pd.DataFrame = field(default_factory=pd.DataFrame)

    reason: str = ""

    processing_time: float = 0.0


# ---------------------------------------------------------------------
# Batch statistics
# ---------------------------------------------------------------------

@dataclass
class ParserStatistics:
    """
    Statistics collected during batch processing.
    """

    total: int = 0

    success: int = 0

    failed: int = 0

    scanned: int = 0

    digital: int = 0

    skipped: int = 0

    camelot_lattice: int = 0

    camelot_stream: int = 0

    pdfplumber: int = 0

    tabula: int = 0

    ocr: int = 0
