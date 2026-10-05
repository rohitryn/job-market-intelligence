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
# LOAD MASTER DATASET
# ==============================

master_file = "data/processed/master_jobs_cleaned.csv"

df = pd.read_csv(master_file)

print("Rows loaded:", len(df))

# Convert missing values to None
df = df.where(pd.notnull(df), None)
# Convert salary_is_predicted to PostgreSQL-compatible boolean
def convert_boolean(value):
    if pd.isna(value):
        return None

    if value in [1, 1.0, True, "1", "1.0", "True", "true"]:
        return True

    if value in [0, 0.0, False, "0", "0.0", "False", "false"]:
        return False

    return None


df["salary_is_predicted"] = df["salary_is_predicted"].apply(
    convert_boolean
)
# ==============================
# LOAD COMPANY / LOCATION IDs
# ==============================

cur.execute("""
    SELECT company_id, company_name
    FROM analytics.companies;
""")

company_map = {
    name: company_id
    for company_id, name in cur.fetchall()
}

cur.execute("""
    SELECT location_id, location_name
    FROM analytics.locations;
""")

location_map = {
    name: location_id
    for location_id, name in cur.fetchall()
}

print("Company mappings:", len(company_map))
print("Location mappings:", len(location_map))

# ==============================
# LOAD JOBS
# ==============================

inserted = 0
skipped = 0

for _, row in df.iterrows():

    company_id = company_map.get(row["company"])
    location_id = location_map.get(row["location"])

    try:

        cur.execute(
            """
            INSERT INTO analytics.jobs (
                source,
                source_job_id,
                job_title,
                company_id,
                location_id,
                category,
                salary_min,
                salary_max,
                salary_is_predicted,
                contract_type,
                contract_time,
                description,
                posting_date,
                job_url,
                latitude,
                longitude,
                collection_query,
                collection_location
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (source, source_job_id)
            DO NOTHING;
            """,
            (
                row["source"],
                str(row["job_id"]),
                row["job_title"],
                company_id,
                location_id,
                row["category"],
                row["salary_min"],
                row["salary_max"],
                row["salary_is_predicted"],
                row["contract_type"],
                row["contract_time"],
                row["description"],
                row["posting_date"],
                row["job_url"],
                row["latitude"],
                row["longitude"],
                row["collection_query"],
                row["collection_location"]
            )
        )

        inserted += cur.rowcount

    except Exception as e:

        skipped += 1

        print(
            f"Error loading job "
            f"{row['job_id']}: {e}"
        )

        conn.rollback()

        # Restore transaction after error
        continue

conn.commit()

# ==============================
# VERIFY
# ==============================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs;
""")

job_count = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs
    WHERE company_id IS NULL;
""")

missing_company = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.jobs
    WHERE location_id IS NULL;
""")

missing_location = cur.fetchone()[0]

print("\n========== JOB LOAD STATUS ==========")
print("Jobs inserted:", inserted)
print("Jobs skipped:", skipped)
print("Jobs in database:", job_count)
print("Missing company:", missing_company)
print("Missing location:", missing_location)

cur.close()
conn.close()