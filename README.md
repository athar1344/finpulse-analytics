# FinPulse Analytics

An end-to-end financial dashboard automation system: raw files land in a folder, get validated, cleaned, feature-engineered, merged into a canonical dataset, visualized in an interactive Streamlit dashboard, and exported as Excel/PDF/CSV reports — all on a schedule.

## 1. Business Understanding

**Business problem.** Finance teams receive monthly Actuals/Budget/Forecast exports per business unit as spreadsheets. Consolidating them, tracking budget variance, and producing leadership reports is manual and error-prone.

**Objectives.**
- Automatically ingest and validate new financial exports.
- Maintain a single clean, de-duplicated dataset over time.
- Give analysts a self-serve, filterable dashboard.
- Generate shareable Excel/PDF/CSV reports on demand or on a schedule.

**KPIs.**
- Total Sales (Actuals)
- Total Expenses (Actuals)
- Net Margin %
- Budget Variance % (Actual vs Budget)
- Year-over-Year Growth %
- Top-performing Business Unit

**Expected outcome.** A refreshable, auditable pipeline plus a dashboard that replaces manual spreadsheet consolidation.

## 2. Architecture

```
finpulse-analytics/
├── data/
│   ├── raw/            # drop new source files here
│   ├── processed/       # canonical cleaned dataset (financials_clean.csv)
│   └── archive/          # source files moved here after successful ingestion
├── dashboard/
│   ├── app.py            # Streamlit entrypoint
│   ├── kpi.py             # KPI calculations
│   ├── charts.py          # Plotly chart builders (14 chart types)
│   └── filters.py         # sidebar navigation + filters
├── automation/
│   ├── refresh.py         # ingest -> validate -> clean -> feature engineer -> merge -> archive
│   ├── scheduler.py        # APScheduler recurring job runner
│   └── report_generator.py # Excel / PDF / CSV report exports
├── utils/
│   ├── cleaning.py         # missing values, duplicates, dtype fixes, standardization
│   ├── preprocessing.py     # feature engineering (totals, quarters, YoY growth)
│   └── helper.py            # logging, file discovery, validation, archiving
├── reports/                 # generated report output
├── logs/                    # rotating pipeline logs
├── config.py                 # paths, constants, thresholds
└── requirements.txt
```

**Data layer.** No database is used. `data/processed/financials_clean.csv` is the single source of truth the dashboard reads. Each refresh appends newly ingested rows, re-cleans the combined dataset, de-duplicates on `(Account, business_unit, Currency, Year, Scenario)`, and re-derives all engineered features so the file is always self-consistent.

**Pipeline flow.** `automation/refresh.py` is the single orchestration entry point, used identically by a manual button click in the dashboard, a direct script run, and the scheduler.

```
data/raw/*.xlsx|csv
   → validate columns & non-empty
   → utils/cleaning.py (dtypes, missing values, standardization, dedupe)
   → utils/preprocessing.py (annual totals, quarters, YoY growth, variance flags)
   → merge with existing data/processed/financials_clean.csv
   → archive source file to data/archive/
   → dashboard reads the refreshed CSV (cached, 5 min TTL)
```

## 3. Technologies Used

| Purpose | Library |
|---|---|
| Dashboard UI | Streamlit |
| Data processing | Pandas, NumPy |
| Charts | Plotly |
| Excel I/O | OpenPyXL |
| PDF reports | ReportLab |
| Scheduling | APScheduler |
| Logging | Python `logging` (rotating file handler) |

## 4. Dashboard Features

- **KPI cards**: Total Sales, Total Expenses, Net Margin %, Budget Variance %, Avg YoY Growth, Top Business Unit
- **Filters**: Year, Business Unit, Scenario (multi-select), free-text Account search
- **Sidebar navigation**: Overview / Trends / Composition / Distribution / Data Explorer
- **Charts**: line, bar, horizontal bar, pie, donut, histogram, scatter, box plot, heatmap, treemap, monthly trend, cumulative ("weekly") trend, top 10, bottom 10, budget-vs-actual grouped bar
- **Data Explorer**: full filtered table, CSV download of the filtered view, one-click Excel/PDF/CSV report generation
- **Manual refresh button**: re-runs the ingestion pipeline against `data/raw/` without leaving the app
- **Caching**: `st.cache_data` with a 5-minute TTL on the processed dataset load

## 5. Automation

`automation/refresh.py` performs the full ingest → clean → store → archive cycle and can be triggered three ways:

1. **Manually**: `python automation/refresh.py`
2. **From the dashboard**: the "Refresh Data" sidebar button
3. **On a schedule**: `python automation/scheduler.py` (runs every `SCHEDULER_INTERVAL_MINUTES`, default 30, configurable in `config.py`)

Every run logs file receipt, cleaning results, dataset updates, refresh completion, and any errors to `logs/pipeline.log` (rotating, 5 backups).

## 6. Reporting

From the **Data Explorer** page, click "Generate Excel + PDF + CSV Reports" to produce timestamped files in `reports/`:
- **Excel**: raw filtered data + a business-unit/year summary sheet, styled headers
- **PDF**: a formatted summary table via ReportLab
- **CSV**: raw filtered export

Reports can also be generated from the command line: `python automation/report_generator.py`.

## 7. Error Handling

- Missing/unsupported files: skipped with a logged error, pipeline continues with remaining files
- Empty datasets: rejected during validation before entering the pipeline
- Missing required columns: file is rejected and logged, not ingested
- Invalid values (bad years, blank identifiers): filtered out during cleaning
- No processed data yet: dashboard shows an instructional warning instead of crashing

## 8. Installation

```bash
git clone <your-repo-url>
cd finpulse-analytics
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 9. Running Locally

```bash
# 1. Ingest the sample data (already placed in data/raw/)
python automation/refresh.py

# 2. Launch the dashboard
streamlit run dashboard/app.py
```

Open the local URL Streamlit prints (typically `http://localhost:8501`).

To add new data later, drop an Excel/CSV file with the same schema into `data/raw/` and either run `python automation/refresh.py` again or click "Refresh Data" in the sidebar.

## 10. Scheduling Automatic Execution

```bash
python automation/scheduler.py
```

This starts a blocking APScheduler process that runs the refresh pipeline immediately, then every `SCHEDULER_INTERVAL_MINUTES` (set in `config.py`). Run it as a background service (e.g. `systemd`, `pm2`, or a `screen`/`tmux` session) in production.

## 11. Deployment

**Streamlit Community Cloud**
1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, set the main file to `dashboard/app.py`.
3. Add `requirements.txt` (already present) — Streamlit Cloud installs it automatically.

**Render / Railway**
1. Create a new Web Service from the GitHub repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0`
4. Optionally add a second background worker service running `python automation/scheduler.py` for scheduled refreshes.

## 12. Extending the Project

- **Database**: swap `data/processed/financials_clean.csv` for SQLAlchemy models against SQLite/PostgreSQL/MySQL — `utils/helper.py` and `automation/refresh.py` are the only files that touch the storage layer.
- **APIs**: wrap `automation/refresh.py` and `automation/report_generator.py` in a FastAPI service to trigger refreshes/reports remotely.
- **Cloud storage**: point `RAW_DATA_DIR`/`PROCESSED_DATA_DIR` in `config.py` at an S3/GCS-mounted path.
- **Authentication**: add `streamlit-authenticator` in front of `dashboard/app.py` for multi-user access control.
- **Email delivery**: extend `report_generator.py` to email generated reports via SMTP after each scheduled run.

## Sample Dataset

`data/raw/financial_data_2023.xlsx` — synthetic financial data with columns `Account, business_unit, Currency, Year, Scenario, Jan…Dec`, covering multiple business units and Actuals/Budget/Forecast scenarios. Run the refresh pipeline once to populate `data/processed/`.

## Future Improvements

- Multi-year sample data to fully exercise YoY growth charts
- Row-level audit trail (who/when a record was ingested)
- Configurable KPI thresholds with alerting
- Dark/light theme toggle
- Unit test suite for `utils/` and `automation/`
