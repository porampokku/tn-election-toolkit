"""
Simple logging utilities.
"""

from pathlib import Path
from datetime import datetime


class Logger:

    def __init__(self, logfile):

        self.path = Path(logfile)

        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, message):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
