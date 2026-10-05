import os
import pandas as pd
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
# LOAD PROCESSED JOB DATA
# ==========================================

jobs_df = pd.read_csv(
    "data/processed_jobs.csv"
)

print("Jobs loaded from CSV:", len(jobs_df))


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

print("Connected to PostgreSQL.")


# ==========================================
# LOAD COMPANY MAPPINGS
# ==========================================

cursor.execute("""
    SELECT company_id, company_name
    FROM analytics.companies;
""")

company_rows = cursor.fetchall()

company_map = {
    name: company_id
    for company_id, name in company_rows
}

print("Company mappings:", len(company_map))


# ==========================================
# LOAD LOCATION MAPPINGS
# ==========================================

cursor.execute("""
    SELECT location_id, location_name
    FROM analytics.locations;
""")

location_rows = cursor.fetchall()

location_map = {
    name: location_id
    for location_id, name in location_rows
}

print("Location mappings:", len(location_map))


# ==========================================
# INSERT JOBS
# ==========================================

insert_query = """
INSERT INTO analytics.jobs (
    job_id,
    job_title,
    company_id,
    location_id,
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
missing_company = 0
missing_location = 0


for _, row in jobs_df.iterrows():

    company_name = row["company"]

    location_name = row["location"]

    company_id = company_map.get(company_name)

    location_id = location_map.get(location_name)


    if pd.notna(company_name) and company_id is None:
        missing_company += 1

    if pd.notna(location_name) and location_id is None:
        missing_location += 1


    cursor.execute(
        insert_query,
        (
            int(row["job_id"]),
            row["job_title"],
            company_id,
            location_id,
            row["category"],
            row["salary_min"],
            row["salary_max"],
            row["description"],
            row["posting_date"],
            row["job_url"],
            row["latitude"],
            row["longitude"]
        )
    )

    inserted_count += cursor.rowcount


# ==========================================
# COMMIT
# ==========================================

connection.commit()

print("\n========== LOAD RESULTS ==========")
print("Jobs inserted:", inserted_count)
print("Missing company mappings:", missing_company)
print("Missing location mappings:", missing_location)


# ==========================================
# VERIFY
# ==========================================

cursor.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs;
""")

job_count = cursor.fetchone()[0]

print("Jobs in PostgreSQL:", job_count)


# ==========================================
# CLOSE CONNECTION
# ==========================================

cursor.close()
connection.close()

print("\nConnection closed.")
print("Jobs loading completed successfully.")