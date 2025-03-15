# NYC Job Market & Hiring Trends Analysis

An end-to-end people analytics portfolio project using the official [Jobs NYC Postings dataset](https://data.cityofnewyork.us/City-Government/Jobs-NYC-Postings/kpav-sd4t). The project turns a live public-sector recruiting snapshot into an auditable Python/SQL workflow, exploratory analysis, six publication-ready charts, and a Power BI-ready reporting model.

## Business problem

Which NYC agencies and occupational groups are hiring, what compensation do they advertise, and how does demand vary by career level and posting period? The analysis deliberately measures job postings separately from advertised positions and does not claim candidate-funnel outcomes that the source cannot support.

## Verified snapshot

The snapshot downloaded on August 18, 2026 contained 2,760 raw records. After removing 9 exact duplicates, the analysis covers **2,751 postings**, **61 agencies**, and **111 source-defined category combinations** from September 4, 2025 through August 18, 2026. Annualized salary midpoint averages **$88,989.82** and has a median of **$82,929**.

Key findings:

- The Department of Health and Mental Hygiene leads with 529 postings; Design & Construction follows with 295.
- Engineering, Architecture, & Planning is the largest category (436 postings), followed by Health (258).
- The top five agencies account for 48.8% of all postings, showing substantial hiring concentration.
- Experienced non-manager roles represent 2,078 postings; entry-level roles represent 320.
- External postings (1,428) slightly exceed internal postings (1,323).
- Among categories with at least 10 postings, Technology, Data & Innovation has the highest median midpoint at $110,000.

These results describe a current-postings snapshot, not all NYC hiring activity or completed hires. Category values can contain multiple source-assigned categories, so 111 reflects distinct published strings rather than a hand-built taxonomy.

## Workflow and data quality

```text
NYC Open Data API -> raw CSV -> Pandas cleaning and QA -> processed CSV + SQLite
                  -> EDA charts -> Power BI CSV + verified resume metrics
```

Cleaning standardizes headers, whitespace, missing markers, agency casing, category separators, numerics, and four date fields. Hourly and daily ranges are annualized using 2,080 hours and 260 days; original salary fields are retained. Derived fields include salary midpoint/band, posting month/year, days open, experience level, and a documented posting key.

The QA report covers nulls, exact and key-level duplicates, missing titles/agencies, invalid dates, reversed/negative salary ranges, high-salary review flags, and source-to-clean row reconciliation. The current run found 9 exact duplicates, 12 repeated candidate posting keys, no invalid salary ranges, no unparseable dates, and no missing salary components. Candidate keys are flagged rather than silently discarded because a Job ID/posting-type pair is not guaranteed to be a source primary key.

## Repository structure

```text
data/raw/                      immutable downloaded snapshot
data/processed/                cleaned dataset and QA JSON
notebooks/                     cleaning/QA and EDA walkthroughs
sql/                           schema, QA checks, and 14 analytical queries
src/                           ingestion, cleaning, metrics/reporting modules
output/charts/                 six PNG charts
output/powerbi/                import-ready CSV and dashboard specification
output/resume_metrics.txt      verified outcomes and resume bullets
run_pipeline.py                end-to-end entry point
```

## Run locally

Requires Python 3.11+ and internet access for the source download.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
```

To refresh individual stages: `python -m src.ingest`, `python -m src.clean`, and `python -m src.metrics`. The pipeline writes `nyc_jobs.db`, so analytical SQL can be run with `sqlite3 nyc_jobs.db < sql/analysis_queries.sql`. The API URL and all output paths are project-relative; the cleaner tolerates optional source columns and fails clearly when required salary or ID fields disappear.

## SQL and Power BI

The SQL library contains 14 analyses using CTEs, CASE expressions, aggregations, window functions, ranking, month-over-month change, a SQLite median pattern, salary validation, and duplicate/null checks. The Power BI specification defines five KPI cards, two report pages, six slicers, DAX measures, grain, salary assumptions, and recommended visuals. Import `output/powerbi/nyc_jobs_powerbi.csv` and follow `output/powerbi/powerbi_dashboard_spec.md`.

## Portfolio outcomes

Verified bullets are generated on every run in `output/resume_metrics.txt`. The current source supports a truthful “2,700+ postings” claim—not “10K+.” This makes the project reproducible and defensible in an interview.

