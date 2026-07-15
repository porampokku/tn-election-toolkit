"""
Configuration settings for the Tamil Nadu Assembly Form 20 Toolkit.
"""

from pathlib import Path

# -----------------------------------------------------------------------------
# Project directories
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "output"
PDF_DIR = OUTPUT_DIR / "PDFs"
DATA_DIR = OUTPUT_DIR / "data"
LOG_DIR = OUTPUT_DIR / "logs"

# -----------------------------------------------------------------------------
# Website
# -----------------------------------------------------------------------------

BASE_URL = "https://elections.tn.gov.in"

COMPLETED_ELECTIONS_URL = (
    "https://elections.tn.gov.in/generalelections_Completed.aspx"
)

ASSEMBLY_PAGES = {
    2026: "https://elections.tn.gov.in/TNLA2026.aspx",
    2021: "https://elections.tn.gov.in/TNLA2021.aspx",
    2016: "https://elections.tn.gov.in/TNLA2016.aspx",
    2011: "https://elections.tn.gov.in/AssemblyElections2011.aspx",
    2006: "https://elections.tn.gov.in/General_Elections_2006.aspx",
}

# -----------------------------------------------------------------------------
# Download settings
# -----------------------------------------------------------------------------

MAX_WORKERS = 12
TIMEOUT = 60
RETRIES = 3

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)
