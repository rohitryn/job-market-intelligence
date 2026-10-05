import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()

print("\n========== DATABASE INTEGRITY CHECK ==========\n")


# ==========================================
# 1. TABLE COUNTS
# ==========================================

tables = [
    "analytics.jobs",
    "analytics.companies",
    "analytics.locations",
    "analytics.skills",
    "analytics.job_skills",
    "analytics.salary_history"
]

for table in tables:

    cur.execute(f"SELECT COUNT(*) FROM {table};")

    count = cur.fetchone()[0]

    print(f"{table:<30} {count}")


# ==========================================
# 2. JOBS WITHOUT COMPANY
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs
    WHERE company_id IS NULL;
""")

missing_company = cur.fetchone()[0]

print("\nJobs without company:", missing_company)


# ==========================================
# 3. JOBS WITHOUT LOCATION
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs
    WHERE location_id IS NULL;
""")

missing_location = cur.fetchone()[0]

print("Jobs without location:", missing_location)


# ==========================================
# 4. JOBS WITH SKILLS
# ==========================================

cur.execute("""
    SELECT COUNT(DISTINCT job_id)
    FROM analytics.job_skills;
""")

jobs_with_skills = cur.fetchone()[0]

print("Jobs with detected skills:", jobs_with_skills)


# ==========================================
# 5. JOBS WITHOUT SKILLS
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs j
    WHERE NOT EXISTS (
        SELECT 1
        FROM analytics.job_skills js
        WHERE js.job_id = j.job_id
    );
""")

jobs_without_skills = cur.fetchone()[0]

print("Jobs without detected skills:", jobs_without_skills)


# ==========================================
# 6. ORPHAN JOB-SKILL RELATIONSHIPS
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.job_skills js
    LEFT JOIN analytics.jobs j
        ON js.job_id = j.job_id
    WHERE j.job_id IS NULL;
""")

orphan_jobs = cur.fetchone()[0]

print("Orphan job relationships:", orphan_jobs)


# ==========================================
# 7. ORPHAN SKILL RELATIONSHIPS
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.job_skills js
    LEFT JOIN analytics.skills s
        ON js.skill_id = s.skill_id
    WHERE s.skill_id IS NULL;
""")

orphan_skills = cur.fetchone()[0]

print("Orphan skill relationships:", orphan_skills)


# ==========================================
# 8. DUPLICATE SOURCE JOBS
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT source, source_job_id
        FROM analytics.jobs
        GROUP BY source, source_job_id
        HAVING COUNT(*) > 1
    ) duplicates;
""")

duplicate_source_jobs = cur.fetchone()[0]

print("Duplicate source jobs:", duplicate_source_jobs)


# ==========================================
# 9. INVALID SALARY RANGES
# ==========================================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs
    WHERE salary_min IS NOT NULL
      AND salary_max IS NOT NULL
      AND salary_min > salary_max;
""")

invalid_salary = cur.fetchone()[0]

print("Invalid salary ranges:", invalid_salary)


# ==========================================
# 10. JOBS BY SOURCE
# ==========================================

print("\n========== JOBS BY SOURCE ==========\n")

cur.execute("""
    SELECT source, COUNT(*)
    FROM analytics.jobs
    GROUP BY source
    ORDER BY COUNT(*) DESC;
""")

for source, count in cur.fetchall():
    print(f"{source:<20} {count}")


# ==========================================
# FINAL STATUS
# ==========================================

print("\n========== FINAL CHECK ==========\n")

checks = {
    "Jobs = 5838": 
        None,

    "Orphan job relationships = 0":
        orphan_jobs == 0,

    "Orphan skill relationships = 0":
        orphan_skills == 0,

    "Duplicate source jobs = 0":
        duplicate_source_jobs == 0,

    "Invalid salary ranges = 0":
        invalid_salary == 0,

    "Jobs with + without skills = total jobs":
        jobs_with_skills + jobs_without_skills == 5838
}

# Check actual job count
cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs;
""")

total_jobs = cur.fetchone()[0]

checks["Jobs = 5838"] = total_jobs == 5838


for check, result in checks.items():

    status = "PASS" if result else "FAIL"

    print(f"{status:<6} {check}")


cur.close()
conn.close()