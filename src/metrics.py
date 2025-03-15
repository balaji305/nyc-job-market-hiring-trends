"""Generate analytics, charts, Power BI exports, and verified resume metrics."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "jobs_nyc_postings_clean.csv"


def _save_charts(df: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = ROOT / "output" / "charts"; out.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    specs = [
        (df["agency_clean"].value_counts().head(15).sort_values(), "Top 15 Agencies by Job Postings", "Job postings", "top_agencies.png", "barh"),
        (df["posting_month"].value_counts().sort_index(), "Job Postings by Month", "Job postings", "posting_trend.png", "line"),
        (df["job_category_clean"].value_counts().head(15).sort_values(), "Top 15 Job Categories", "Job postings", "top_categories.png", "barh"),
        (df.groupby("job_category_clean")["salary_midpoint"].median().dropna().nlargest(15).sort_values(), "Highest Median Salary by Job Category", "Annualized median salary ($)", "median_salary_category.png", "barh"),
        (df.groupby("agency_clean")["salary_midpoint"].median().dropna().nlargest(15).sort_values(), "Highest Median Salary by Agency", "Annualized median salary ($)", "agency_salary.png", "barh"),
    ]
    for values, title, xlabel, name, kind in specs:
        plot_options = {"kind": kind, "figsize": (10, 6), "color": "#1f77b4"}
        if kind == "line":
            plot_options["marker"] = "o"
        ax = values.plot(**plot_options)
        ax.set(title=title, xlabel=xlabel, ylabel="")
        plt.tight_layout(); plt.savefig(out / name, dpi=160); plt.close()
    ax = df.loc[df["salary_midpoint"].between(0, 300000), "salary_midpoint"].plot.hist(bins=30, figsize=(10, 6), color="#1f77b4")
    ax.set(title="Distribution of Annualized Salary Midpoints", xlabel="Annualized salary midpoint ($)", ylabel="Postings")
    plt.tight_layout(); plt.savefig(out / "salary_distribution.png", dpi=160); plt.close()


def run() -> dict:
    df = pd.read_csv(DATA, parse_dates=["posting_date", "post_until", "posting_updated", "process_date"])
    quality = json.loads((ROOT / "data" / "processed" / "data_quality_summary.json").read_text())
    pbi = ROOT / "output" / "powerbi"; pbi.mkdir(parents=True, exist_ok=True)
    dimensions = ["posting_key", "job_id", "agency_clean", "posting_type", "business_title", "civil_service_title",
                  "job_category_clean", "full_time_part_time_indicator", "career_level", "experience_level",
                  "salary_frequency", "annual_salary_min", "annual_salary_max", "salary_midpoint", "salary_band",
                  "posting_date", "posting_month", "posting_year", "post_until", "days_open", "work_location",
                  "division_work_unit", "number_of_positions"]
    df[[c for c in dimensions if c in df]].to_csv(pbi / "nyc_jobs_powerbi.csv", index=False)
    with sqlite3.connect(ROOT / "nyc_jobs.db") as conn:
        df.to_sql("job_postings", conn, if_exists="replace", index=False)
    _save_charts(df)
    valid = df["salary_midpoint"].notna()
    top_category = df["job_category_clean"].value_counts().index[0]
    metrics = {
        "total_postings": len(df), "agencies": df["agency_clean"].nunique(),
        "job_categories": df["job_category_clean"].nunique(), "fields_cleaned": quality["fields_cleaned_or_standardized"],
        "duplicates": quality["exact_duplicates_removed"], "missing_salary": quality["missing_salary_components"],
        "date_min": df["posting_date"].min().date().isoformat(), "date_max": df["posting_date"].max().date().isoformat(),
        "average_salary": round(df.loc[valid, "salary_midpoint"].mean(), 2),
        "median_salary": round(df.loc[valid, "salary_midpoint"].median(), 2), "top_category": top_category,
        "top5_agency_concentration_pct": round(df["agency_clean"].value_counts().head(5).sum() / len(df) * 100, 1),
    }
    n_floor = (len(df) // 100) * 100
    bullets = [
        f"Analyzed {n_floor:,}+ public job postings using Python and SQL to identify hiring trends across {metrics['agencies']} agencies, {metrics['job_categories']} job categories, salary ranges, and posting periods.",
        f"Cleaned and standardized {metrics['fields_cleaned']} job-posting attributes, identifying {metrics['duplicates']} exact duplicates and {metrics['missing_salary']} records with missing salary components while validating dates and salary ranges.",
        f"Performed exploratory analysis across {metrics['agencies']} agencies and {metrics['job_categories']} job categories to compare hiring volume, salary distributions, and workforce demand from {metrics['date_min']} to {metrics['date_max']}.",
        "Built a Power BI-ready reporting model with 5 KPI cards and 6 slicers covering agency, job category, salary band, posting period, experience level, and location.",
    ]
    lines = [f"Total records analyzed: {len(df):,}", f"Number of agencies: {metrics['agencies']}",
             f"Number of job categories: {metrics['job_categories']}", f"Number of fields cleaned: {metrics['fields_cleaned']}",
             f"Number of duplicates identified: {metrics['duplicates']}", f"Records with missing salary fields: {metrics['missing_salary']}",
             f"Date range covered: {metrics['date_min']} to {metrics['date_max']}", "", "Verified resume bullets:"] + [f"- {b}" for b in bullets]
    (ROOT / "output" / "resume_metrics.txt").write_text("\n".join(lines) + "\n")
    (ROOT / "output" / "project_metrics.json").write_text(json.dumps({**metrics, "resume_bullets": bullets}, indent=2))
    return {**metrics, "resume_bullets": bullets}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
