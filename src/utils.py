"""
Utility functions for the Tamil Nadu Assembly Form 20 Toolkit.
"""

from pathlib import Path
import logging
import re
from typing import Union


def create_directory(path: Union[str, Path]) -> Path:
    """
    Create a directory if it does not already exist.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitise_filename(name: str) -> str:
    """
    Remove characters that are invalid in filenames.
    """
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    return name.strip()


def setup_logger(log_file: Union[str, Path]) -> logging.Logger:
    """
    Create and return a logger.
    """
    logger = logging.getLogger("TNForm20")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def file_exists(path: Union[str, Path]) -> bool:
    """
    Return True if the file exists.
    """
    return Path(path).is_file()


def sizeof_mb(path: Union[str, Path]) -> float:
    """
    Return file size in MB.
    """
    path = Path(path)

    if not path.exists():
        return 0.0

    return round(path.stat().st_size / (1024 * 1024), 2)
