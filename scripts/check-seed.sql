-- Checks the seeded data against the S4 and S5 rules. Every "bad" count should be 0.

SELECT 'users' AS check, count(*)::text AS result FROM users
UNION ALL
SELECT 'users without a job (bad)', count(*)::text FROM users u
    WHERE NOT EXISTS (SELECT 1 FROM jobs j WHERE j.user_id = u.id)
UNION ALL
SELECT 'users without a college (bad)', count(*)::text FROM users u
    WHERE NOT EXISTS (SELECT 1 FROM educations e WHERE e.user_id = u.id)
UNION ALL
SELECT 'overlapping jobs (bad)', count(*)::text FROM (
    SELECT start_year,
           lag(end_year) OVER (PARTITION BY user_id ORDER BY start_year, end_year NULLS LAST) AS previous_end,
           lag(user_id) OVER (PARTITION BY user_id ORDER BY start_year, end_year NULLS LAST) AS has_previous
    FROM jobs
) t WHERE has_previous IS NOT NULL AND (previous_end IS NULL OR start_year < previous_end)
UNION ALL
SELECT 'spellings of IIT Bombay', string_agg(DISTINCT college_name, ', ') FROM educations
    WHERE college_name IN ('IIT Bombay', 'IITB', 'IIT-Bombay')
UNION ALL
SELECT 'share of jobs at top 1% companies', round(100.0 * sum(n) FILTER (WHERE rank <= greatest(1, total / 100)) / sum(n), 1)::text || '%'
    FROM (SELECT count(*) AS n, row_number() OVER (ORDER BY count(*) DESC) AS rank, count(*) OVER () AS total
          FROM jobs GROUP BY company_id) t;
