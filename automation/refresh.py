"""Detect new raw files, validate, clean, engineer features, merge into the
processed dataset, and archive the source files. This is the single entry
point used by both manual runs and the scheduler."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import config
from utils.cleaning import clean_dataframe
from utils.preprocessing import engineer_features
from utils.helper import (
    get_logger,
    list_raw_files,
    read_source_file,
    validate_columns,
    archive_file,
)

logger = get_logger("refresh")


def load_existing_processed() -> pd.DataFrame:
    if os.path.exists(config.PROCESSED_FILE_PATH):
        return pd.read_csv(config.PROCESSED_FILE_PATH)
    return pd.DataFrame()


def ingest_new_files() -> pd.DataFrame:
    raw_files = list_raw_files()
    if not raw_files:
        logger.info("No new files detected in data/raw")
        return pd.DataFrame()

    collected = []
    for file_path in raw_files:
        logger.info("File received: %s", os.path.basename(file_path))
        try:
            df = read_source_file(file_path)
        except Exception as exc:
            logger.error("Failed to read %s: %s", file_path, exc)
            continue

        is_valid, message = validate_columns(df, file_path)
        if not is_valid:
            logger.error("Validation failed: %s", message)
            continue

        collected.append(df)
        archived_path = archive_file(file_path)
        logger.info("Archived %s -> %s", os.path.basename(file_path), archived_path)

    if not collected:
        return pd.DataFrame()

    return pd.concat(collected, ignore_index=True)


def run_refresh() -> dict:
    logger.info("Starting data refresh pipeline")

    new_data = ingest_new_files()
    if new_data.empty:
        logger.info("Refresh finished with no new data")
        return {"status": "no_new_data", "rows_added": 0}

    cleaned, duplicates_removed = clean_dataframe(new_data)
    logger.info("Cleaning completed | rows=%d | duplicates_removed=%d", len(cleaned), duplicates_removed)

    enriched = engineer_features(cleaned)

    existing = load_existing_processed()
    combined = pd.concat([existing, enriched], ignore_index=True) if not existing.empty else enriched
    combined, final_duplicates = clean_dataframe(combined)
    combined = engineer_features(combined.drop(
        columns=[c for c in ["annual_total", "Q1", "Q2", "Q3", "Q4", "is_actual",
                              "is_budget_or_forecast", "yoy_growth_pct"] if c in combined.columns]
    ))

    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    combined.to_csv(config.PROCESSED_FILE_PATH, index=False)
    logger.info("Database updated | total_rows=%d | file=%s", len(combined), config.PROCESSED_FILE_PATH)
    logger.info("Dashboard refreshed")

    return {"status": "success", "rows_added": len(enriched), "total_rows": len(combined)}


if __name__ == "__main__":
    result = run_refresh()
    print(result)
