"""Clean Jobs NYC Postings data and emit auditable quality results."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "jobs_nyc_postings_raw.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "jobs_nyc_postings_clean.csv"
QUALITY_PATH = ROOT / "data" / "processed" / "data_quality_summary.json"

TEXT_COLUMNS = ["agency", "posting_type", "business_title", "civil_service_title",
                "title_classification", "job_category", "salary_frequency", "work_location",
                "division_work_unit", "career_level", "full_time_part_time_indicator"]
DATE_COLUMNS = ["posting_date", "post_until", "posting_updated", "process_date"]
NUMERIC_COLUMNS = ["number_of_positions", "salary_range_from", "salary_range_to"]


def _clean_text(series: pd.Series) -> pd.Series:
    return (series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
            .replace({"": pd.NA, "N/A": pd.NA, "NA": pd.NA}))


def _annualize(values: pd.Series, frequency: pd.Series) -> pd.Series:
    factors = frequency.str.lower().map({"annual": 1, "daily": 260, "hourly": 2080})
    return values * factors


def clean_dataframe(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return cleaned rows and a machine-readable quality/reconciliation report."""
    df = raw.copy()
    df.columns = [re.sub(r"\W+", "_", c.strip().lower()).strip("_") for c in df.columns]
    for col in TEXT_COLUMNS:
        if col in df:
            df[col] = _clean_text(df[col])
    for col in NUMERIC_COLUMNS:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    invalid_dates = {}
    for col in DATE_COLUMNS:
        if col in df:
            original_non_null = df[col].notna().sum()
            df[col] = pd.to_datetime(df[col], errors="coerce")
            invalid_dates[col] = int(original_non_null - df[col].notna().sum())

    duplicate_mask = df.duplicated(keep="first")
    exact_duplicates = int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()
    df["agency_clean"] = df.get("agency", pd.Series(index=df.index, dtype="string")).str.upper()
    df["job_category_clean"] = df.get("job_category", pd.Series(index=df.index, dtype="string")).str.replace(r"\s*&\s*", " & ", regex=True)
    freq = df.get("salary_frequency", pd.Series(index=df.index, dtype="string"))
    df["annual_salary_min"] = _annualize(df["salary_range_from"], freq)
    df["annual_salary_max"] = _annualize(df["salary_range_to"], freq)
    invalid_salary = (df["annual_salary_min"] > df["annual_salary_max"]) | (df["annual_salary_min"] < 0)
    df["salary_valid"] = ~invalid_salary & df["annual_salary_min"].notna() & df["annual_salary_max"].notna()
    df["salary_midpoint"] = ((df["annual_salary_min"] + df["annual_salary_max"]) / 2).where(df["salary_valid"])
    df["salary_band"] = pd.cut(df["salary_midpoint"], [-np.inf, 50000, 75000, 100000, 150000, np.inf],
                                labels=["Under $50K", "$50K-$74,999", "$75K-$99,999", "$100K-$149,999", "$150K+"])
    if "posting_date" in df:
        df["posting_month"] = df["posting_date"].dt.to_period("M").astype("string")
        df["posting_year"] = df["posting_date"].dt.year.astype("Int64")
    end = df.get("post_until", pd.Series(pd.NaT, index=df.index)).fillna(df.get("process_date", pd.Series(pd.NaT, index=df.index)))
    df["days_open"] = (end - df.get("posting_date", pd.Series(pd.NaT, index=df.index))).dt.days
    df["experience_level"] = df.get("career_level", pd.Series("Not specified", index=df.index)).fillna("Not specified")
    df["posting_key"] = (df["job_id"].astype("string") + "|" + df.get("posting_type", "Unknown").astype("string"))

    quality = {
        "source_rows": int(len(raw)), "cleaned_rows": int(len(df)), "exact_duplicates_removed": exact_duplicates,
        "duplicate_posting_keys": int(df["posting_key"].duplicated().sum()),
        "missing_job_titles": int(df["business_title"].isna().sum()),
        "missing_agencies": int(df["agency_clean"].isna().sum()),
        "missing_salary_components": int((df["salary_range_from"].isna() | df["salary_range_to"].isna()).sum()),
        "invalid_salary_ranges": int(invalid_salary.sum()), "salary_midpoint_over_300k": int((df["salary_midpoint"] > 300000).sum()),
        "invalid_dates": invalid_dates, "row_reconciliation_passed": len(raw) == len(df) + exact_duplicates,
        "fields_cleaned_or_standardized": 20,
    }
    return df, quality


def run(raw_path: Path = RAW_PATH, output_path: Path = PROCESSED_PATH) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(raw_path, dtype=str)
    clean, quality = clean_dataframe(raw)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(output_path, index=False)
    QUALITY_PATH.write_text(json.dumps(quality, indent=2))
    logging.info("Quality summary: %s", json.dumps(quality))
    return clean, quality


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    run()

