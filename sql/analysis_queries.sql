-- Q1: Top 10 agencies by posting volume
SELECT agency_clean, COUNT(*) postings, SUM(COALESCE(number_of_positions, 0)) vacancies
FROM job_postings GROUP BY agency_clean ORDER BY postings DESC LIMIT 10;

-- Q2: Top job categories
SELECT job_category_clean, COUNT(*) postings
FROM job_postings GROUP BY job_category_clean ORDER BY postings DESC LIMIT 10;

-- Q3: Average and median-like salary (SQLite window functions)
WITH ranked AS (
 SELECT salary_midpoint, ROW_NUMBER() OVER (ORDER BY salary_midpoint) rn,
        COUNT(*) OVER () n FROM job_postings WHERE salary_midpoint IS NOT NULL
)
SELECT ROUND(AVG(salary_midpoint),2) median_salary,
       (SELECT ROUND(AVG(salary_midpoint),2) FROM job_postings WHERE salary_midpoint IS NOT NULL) average_salary
FROM ranked WHERE rn IN ((n+1)/2, (n+2)/2);

-- Q4: Monthly hiring trend with month-over-month change
WITH monthly AS (
 SELECT posting_month, COUNT(*) postings FROM job_postings
 WHERE posting_month IS NOT NULL GROUP BY posting_month
), trend AS (
 SELECT *, LAG(postings) OVER (ORDER BY posting_month) prior_month FROM monthly
)
SELECT *, ROUND(100.0 * (postings-prior_month)/NULLIF(prior_month,0),1) mom_pct
FROM trend ORDER BY posting_month;

-- Q5: Highest-paying categories (minimum 10 postings)
SELECT job_category_clean, COUNT(*) postings, ROUND(AVG(salary_midpoint),2) average_salary
FROM job_postings WHERE salary_midpoint IS NOT NULL
GROUP BY job_category_clean HAVING COUNT(*) >= 10 ORDER BY average_salary DESC LIMIT 10;

-- Q6: Salary-band distribution
SELECT salary_band, COUNT(*) postings,
 ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM job_postings WHERE salary_band IS NOT NULL),1) pct
FROM job_postings WHERE salary_band IS NOT NULL GROUP BY salary_band ORDER BY MIN(salary_midpoint);

-- Q7: Agency-level salary comparison
SELECT agency_clean, COUNT(salary_midpoint) salaried_postings,
 ROUND(AVG(salary_midpoint),2) average_salary, ROUND(MIN(salary_midpoint),2) minimum,
 ROUND(MAX(salary_midpoint),2) maximum
FROM job_postings GROUP BY agency_clean HAVING COUNT(salary_midpoint)>=10 ORDER BY average_salary DESC;

-- Q8: Duplicate detection
SELECT posting_key, COUNT(*) occurrences FROM job_postings
GROUP BY posting_key HAVING COUNT(*) > 1 ORDER BY occurrences DESC;

-- Q9: Null profile
SELECT COUNT(*) rows_total, SUM(agency_clean IS NULL) agency_nulls,
 SUM(business_title IS NULL) title_nulls, SUM(job_category_clean IS NULL) category_nulls,
 SUM(salary_midpoint IS NULL) salary_nulls FROM job_postings;

-- Q10: Salary validation
SELECT COUNT(*) invalid_ranges FROM job_postings
WHERE annual_salary_min > annual_salary_max OR annual_salary_min < 0;

-- Q11: Category trends by month, ranked within month
WITH counts AS (
 SELECT posting_month, job_category_clean, COUNT(*) postings
 FROM job_postings GROUP BY posting_month, job_category_clean
)
SELECT *, DENSE_RANK() OVER (PARTITION BY posting_month ORDER BY postings DESC) category_rank
FROM counts ORDER BY posting_month, category_rank;

-- Q12: Rank agencies by volume and compensation
WITH agency AS (
 SELECT agency_clean, COUNT(*) postings, AVG(salary_midpoint) average_salary
 FROM job_postings GROUP BY agency_clean
)
SELECT *, DENSE_RANK() OVER (ORDER BY postings DESC) volume_rank,
 DENSE_RANK() OVER (ORDER BY average_salary DESC) salary_rank FROM agency;

-- Q13: Internal vs external posting mix
SELECT posting_type, COUNT(*) postings, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (),1) pct
FROM job_postings GROUP BY posting_type;

-- Q14: Full-time/part-time and career-level demand
SELECT CASE full_time_part_time_indicator WHEN 'F' THEN 'Full-time' WHEN 'P' THEN 'Part-time' ELSE 'Unknown' END employment_type,
 experience_level, COUNT(*) postings
FROM job_postings GROUP BY employment_type, experience_level ORDER BY postings DESC;

