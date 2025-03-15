-- 1. Nulls in required analytical dimensions
SELECT SUM(job_id IS NULL) missing_job_ids,
       SUM(business_title IS NULL OR TRIM(business_title) = '') missing_titles,
       SUM(agency_clean IS NULL OR TRIM(agency_clean) = '') missing_agencies,
       SUM(salary_midpoint IS NULL) missing_salary_midpoints
FROM job_postings;

-- 2. Duplicate row-grain candidates
SELECT posting_key, COUNT(*) occurrences
FROM job_postings GROUP BY posting_key HAVING COUNT(*) > 1;

-- 3. Salary range validation
SELECT posting_key, salary_range_from, salary_range_to, salary_frequency
FROM job_postings
WHERE annual_salary_min > annual_salary_max OR annual_salary_min < 0;

-- 4. Date validation
SELECT posting_key, posting_date, post_until
FROM job_postings
WHERE posting_date IS NULL OR (post_until IS NOT NULL AND post_until < posting_date);

-- 5. Suspicious annualized salary outliers (review, do not automatically delete)
SELECT posting_key, business_title, salary_midpoint
FROM job_postings WHERE salary_midpoint > 300000 ORDER BY salary_midpoint DESC;

-- 6. Category consistency / whitespace check
SELECT job_category_clean, COUNT(*)
FROM job_postings
WHERE job_category_clean <> TRIM(job_category_clean)
GROUP BY job_category_clean;

