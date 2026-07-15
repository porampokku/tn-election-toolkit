"""
Parser entry point.
"""

from __future__ import annotations

from src.engines.camelot_lattice import parse_with_camelot_lattice


def parse_pdf(pdf_path):
    """
    Parse one Form 20 PDF.
    """

    return parse_with_camelot_lattice(pdf_path)
