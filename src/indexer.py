"""
Build cleaned dataframes from Form 20 PDFs.
"""

from __future__ import annotations

import time
import traceback
from pathlib import Path

from src.models import ProcessResult
from src.parser import parse_pdf
from src.transformer import transform


def process_pdf(pdf_path: str | Path) -> ProcessResult:
    """
    Parse one Form 20 PDF and return a ProcessResult.
    """

    start = time.perf_counter()

    pdf_path = Path(pdf_path)

    try:

        metadata, dataframe = parse_pdf(pdf_path)

        dataframe = transform(dataframe)

        elapsed = time.perf_counter() - start

        return ProcessResult(
            success=True,
            parser="camelot_lattice",
            metadata=metadata,
            dataframe=dataframe,
            processing_time=elapsed,
        )

    except Exception as e:

        traceback.print_exc()

        elapsed = time.perf_counter() - start

        return ProcessResult(
            success=False,
            parser="camelot_lattice",
            reason=str(e),
            processing_time=elapsed,
        )
