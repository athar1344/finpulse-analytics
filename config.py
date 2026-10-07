"""Central configuration for paths, constants, and thresholds."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
ARCHIVE_DATA_DIR = os.path.join(DATA_DIR, "archive")

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

PROCESSED_FILE_NAME = "financials_clean.csv"
PROCESSED_FILE_PATH = os.path.join(PROCESSED_DATA_DIR, PROCESSED_FILE_NAME)

LOG_FILE_PATH = os.path.join(LOGS_DIR, "pipeline.log")

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".xls")

REQUIRED_COLUMNS = [
    "Account",
    "business_unit",
    "Currency",
    "Year",
    "Scenario",
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

MONTH_COLUMNS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

DEDUPE_KEYS = ["Account", "business_unit", "Currency", "Year", "Scenario"]

SCHEDULER_INTERVAL_MINUTES = 30

for _dir in (RAW_DATA_DIR, PROCESSED_DATA_DIR, ARCHIVE_DATA_DIR, REPORTS_DIR, LOGS_DIR):
    os.makedirs(_dir, exist_ok=True)
