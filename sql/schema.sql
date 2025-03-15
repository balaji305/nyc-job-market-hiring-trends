-- SQLite schema. The Python pipeline creates and loads this table automatically.
CREATE TABLE IF NOT EXISTS job_postings (
  posting_key TEXT, job_id TEXT, agency TEXT, posting_type TEXT,
  number_of_positions REAL, business_title TEXT, civil_service_title TEXT,
  title_classification TEXT, title_code_no TEXT, level TEXT, job_category TEXT,
  full_time_part_time_indicator TEXT, career_level TEXT,
  salary_range_from REAL, salary_range_to REAL, salary_frequency TEXT,
  work_location TEXT, division_work_unit TEXT, posting_date TEXT,
  post_until TEXT, posting_updated TEXT, process_date TEXT,
  agency_clean TEXT, job_category_clean TEXT, annual_salary_min REAL,
  annual_salary_max REAL, salary_valid INTEGER, salary_midpoint REAL,
  salary_band TEXT, posting_month TEXT, posting_year INTEGER,
  days_open REAL, experience_level TEXT
);

-- Manual SQLite load option:
-- .mode csv
-- .import --skip 1 data/processed/jobs_nyc_postings_clean.csv job_postings

