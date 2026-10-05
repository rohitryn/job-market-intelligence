import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ==============================
# DATABASE CONNECTION
# ==============================

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()

# ==============================
# LOAD SKILL EXTRACTION
# ==============================

skills_file = "data/processed/job_skills_extracted.csv"

skills_df = pd.read_csv(skills_file)

print("Skill extraction rows:", len(skills_df))
print("Skill extraction columns:", skills_df.columns.tolist())


# ==============================
# LOAD MASTER DATASET
# ==============================

master_file = "data/processed/master_jobs_cleaned.csv"

master_df = pd.read_csv(master_file)

print("Master dataset rows:", len(master_df))


# ==============================
# BUILD SOURCE-AWARE JOB MAP
# ==============================

job_source_map = (
    master_df[
        ["job_id", "source"]
    ]
    .drop_duplicates()
)

job_source_map["job_id"] = job_source_map["job_id"].astype(str)

# Convert to dictionary:
# source job ID -> source

source_map = dict(
    zip(
        job_source_map["job_id"],
        job_source_map["source"]
    )
)

print("Source mappings:", len(source_map))


# ==============================
# LOAD DATABASE JOB MAPPING
# ==============================

cur.execute("""
    SELECT job_id, source, source_job_id
    FROM analytics.jobs;
""")

job_map = {
    (source, str(source_job_id)): job_id
    for job_id, source, source_job_id in cur.fetchall()
}

print("Jobs available in database:", len(job_map))


# ==============================
# LOAD SKILL MAPPING
# ==============================

cur.execute("""
    SELECT skill_id, skill_name
    FROM analytics.skills;
""")

skill_map = {
    skill_name: skill_id
    for skill_id, skill_name in cur.fetchall()
}

print("Skills available:", len(skill_map))


# ==============================
# INSERT RELATIONSHIPS
# ==============================

inserted = 0
missing_jobs = 0
missing_skills = 0

for _, row in skills_df.iterrows():

    source_job_id = str(row["job_id"])
    skill_name = row["skill"]

    # Find source from master dataset
    source = source_map.get(source_job_id)

    if source is None:
        missing_jobs += 1
        continue

    # Find internal PostgreSQL job_id
    internal_job_id = job_map.get(
        (source, source_job_id)
    )

    if internal_job_id is None:
        missing_jobs += 1
        continue

    # Find skill_id
    skill_id = skill_map.get(skill_name)

    if skill_id is None:
        missing_skills += 1
        continue

    cur.execute(
        """
        INSERT INTO analytics.job_skills (
            job_id,
            skill_id
        )
        VALUES (%s, %s)
        ON CONFLICT (job_id, skill_id)
        DO NOTHING;
        """,
        (
            internal_job_id,
            skill_id
        )
    )

    inserted += cur.rowcount


conn.commit()


# ==============================
# VERIFY
# ==============================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.job_skills;
""")

relationship_count = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(DISTINCT job_id)
    FROM analytics.job_skills;
""")

jobs_with_skills = cur.fetchone()[0]


print("\n========== JOB-SKILL LOAD STATUS ==========")
print("Relationships inserted:", inserted)
print("Relationships in database:", relationship_count)
print("Jobs with skills:", jobs_with_skills)
print("Missing jobs:", missing_jobs)
print("Missing skills:", missing_skills)


cur.close()
conn.close()