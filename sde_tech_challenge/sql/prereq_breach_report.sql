
-- prereq_breach_report.sql
-- Identify participants registered without completing prerequisites

WITH course_prereqs AS (
    SELECT c.course_id, CAST(j.value AS INTEGER) AS prereq_id
    FROM courses c, json_each(c.prerequisites) j
),
missing_reqs AS (
    SELECT e.enrollment_id, e.participant_id, e.participant_name, e.course_id, e.course_date, cp.prereq_id
    FROM enrollments e
    JOIN course_prereqs cp ON e.course_id = cp.course_id
    LEFT JOIN enrollments completed ON completed.participant_id=e.participant_id
        AND completed.course_id=cp.prereq_id
        AND date(completed.course_date)<date(e.course_date)
    WHERE completed.enrollment_id IS NULL
)
SELECT enrollment_id, participant_id, participant_name, course_id, course_date,
       GROUP_CONCAT(prereq_id) AS missing_prereqs_list,
       COUNT(*) AS missing_reqs_count
FROM missing_reqs
GROUP BY enrollment_id, participant_id, participant_name, course_id, course_date
ORDER BY participant_id, course_date, course_id;
