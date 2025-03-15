# Power BI Dashboard Specification

## Data model

Import `nyc_jobs_powerbi.csv` as `Job Postings`. The table is at posting grain (`posting_key`), with annualized salary values. Use `posting_key` for distinct posting counts and `number_of_positions` for advertised vacancies; do not conflate the two.

## Measures (DAX)

```DAX
Total Job Postings = DISTINCTCOUNT('Job Postings'[posting_key])
Hiring Agencies = DISTINCTCOUNT('Job Postings'[agency_clean])
Median Salary = MEDIAN('Job Postings'[salary_midpoint])
Average Salary = AVERAGE('Job Postings'[salary_midpoint])
Advertised Positions = SUM('Job Postings'[number_of_positions])
Top Hiring Category =
VAR T = TOPN(1, SUMMARIZE('Job Postings', 'Job Postings'[job_category_clean], "N", [Total Job Postings]), [N], DESC)
RETURN CONCATENATEX(T, 'Job Postings'[job_category_clean], ", ")
```

## Page 1 — Market overview

- KPI cards: Total Job Postings, Hiring Agencies, Median Salary, Average Salary, Top Hiring Category.
- Line chart: `posting_month` vs Total Job Postings.
- Bar chart: `agency_clean` vs Total Job Postings (Top N = 10).
- Treemap: `job_category_clean` vs Total Job Postings.

## Page 2 — Compensation and role mix

- Column chart: `salary_band` vs Total Job Postings; sort by `salary_midpoint`.
- Bar chart: median `salary_midpoint` by `job_category_clean` (Top N and minimum volume filter recommended).
- Matrix: agency, category, postings, median salary, advertised positions.
- Slicers: agency, job category, salary band, posting month/year, experience level, work location.

Salary comparisons exclude null/invalid values automatically. Add a tooltip clarifying annualization assumptions: hourly × 2,080 and daily × 260.

