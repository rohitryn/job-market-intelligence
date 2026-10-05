import os
import json
import glob

import psycopg2
from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==========================================
# LOAD RAW JSON FILES
# ==========================================

files = glob.glob("data/raw/*.json")

print("Raw files found:", len(files))

all_jobs = []

for file in files:

    print("Reading:", file)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

        if isinstance(data, dict):
            jobs = data.get("results", [])
        else:
            jobs = data

        all_jobs.extend(jobs)


print("Total raw records:", len(all_jobs))


# ==========================================
# REMOVE DUPLICATE JOBS
# ==========================================

unique_jobs = {}

for job in all_jobs:

    job_id = job.get("id")

    if job_id:
        unique_jobs[job_id] = job


jobs = list(unique_jobs.values())

print("Unique jobs:", len(jobs))


# ==========================================
# CONNECT TO POSTGRESQL
# ==========================================

connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = connection.cursor()

print("\nConnected to PostgreSQL.")


# ==========================================
# INSERT DATA
# ==========================================

insert_query = """
INSERT INTO staging.raw_jobs (
    job_id,
    job_title,
    company,
    location,
    category,
    salary_min,
    salary_max,
    description,
    posting_date,
    job_url,
    latitude,
    longitude
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s
)
ON CONFLICT (job_id)
DO NOTHING;
"""


inserted_count = 0


for job in jobs:

    job_id = job.get("id")

    job_title = job.get("title")

    company = job.get("company", {}).get("display_name")

    location = job.get("location", {}).get("display_name")

    category = job.get("category", {}).get("label")

    salary_min = job.get("salary_min")

    salary_max = job.get("salary_max")

    description = job.get("description")

    posting_date = job.get("created")

    job_url = job.get("redirect_url")

    latitude = job.get("latitude")

    longitude = job.get("longitude")


    cursor.execute(
        insert_query,
        (
            job_id,
            job_title,
            company,
            location,
            category,
            salary_min,
            salary_max,
            description,
            posting_date,
            job_url,
            latitude,
            longitude
        )
    )

    inserted_count += cursor.rowcount


# ==========================================
# COMMIT
# ==========================================

connection.commit()

print("\nRows inserted:", inserted_count)


# ==========================================
# VERIFY
# ==========================================

cursor.execute(
    "SELECT COUNT(*) FROM staging.raw_jobs;"
)

total_rows = cursor.fetchone()[0]

print("Rows currently in staging.raw_jobs:", total_rows)


# ==========================================
# CLOSE CONNECTION
# ==========================================

cursor.close()
connection.close()

print("\nPostgreSQL connection closed.")
print("Raw job loading completed successfully.")