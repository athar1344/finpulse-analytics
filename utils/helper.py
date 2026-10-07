"""Shared helpers: logging setup and raw file validation."""
import logging
import os
import shutil
from logging.handlers import RotatingFileHandler

import pandas as pd

import config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        config.LOG_FILE_PATH, maxBytes=2_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def list_raw_files() -> list:
    if not os.path.isdir(config.RAW_DATA_DIR):
        return []
    files = [
        os.path.join(config.RAW_DATA_DIR, f)
        for f in os.listdir(config.RAW_DATA_DIR)
        if f.lower().endswith(config.SUPPORTED_EXTENSIONS)
    ]
    return sorted(files)


def read_source_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path)
    raise ValueError(f"Unsupported file extension: {ext}")


def validate_columns(df: pd.DataFrame, file_path: str) -> tuple:
    missing = [c for c in config.REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return False, f"{os.path.basename(file_path)} is missing columns: {missing}"
    if df.empty:
        return False, f"{os.path.basename(file_path)} contains no rows"
    return True, ""


def archive_file(file_path: str) -> str:
    os.makedirs(config.ARCHIVE_DATA_DIR, exist_ok=True)
    dest = os.path.join(config.ARCHIVE_DATA_DIR, os.path.basename(file_path))
    if os.path.exists(dest):
        base, ext = os.path.splitext(dest)
        dest = f"{base}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}{ext}"
    shutil.move(file_path, dest)
    return dest
