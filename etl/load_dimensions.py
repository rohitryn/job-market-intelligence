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
# LOAD CSV FILES
# ==========================================

companies_df = pd.read_csv(
    "data/processed/companies.csv"
)

locations_df = pd.read_csv(
    "data/processed/locations.csv"
)

print("Companies loaded from CSV:", len(companies_df))
print("Locations loaded from CSV:", len(locations_df))


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
# INSERT COMPANIES
# ==========================================

company_query = """
INSERT INTO analytics.companies (
    company_id,
    company_name
)
VALUES (%s, %s)
ON CONFLICT (company_id)
DO NOTHING;
"""

company_inserted = 0

for _, row in companies_df.iterrows():

    cursor.execute(
        company_query,
        (
            int(row["company_id"]),
            row["company_name"]
        )
    )

    company_inserted += cursor.rowcount


# ==========================================
# INSERT LOCATIONS
# ==========================================

location_query = """
INSERT INTO analytics.locations (
    location_id,
    location_name
)
VALUES (%s, %s)
ON CONFLICT (location_id)
DO NOTHING;
"""

location_inserted = 0

for _, row in locations_df.iterrows():

    cursor.execute(
        location_query,
        (
            int(row["location_id"]),
            row["location_name"]
        )
    )

    location_inserted += cursor.rowcount


# ==========================================
# COMMIT
# ==========================================

connection.commit()

print("\nCompanies inserted:", company_inserted)
print("Locations inserted:", location_inserted)


# ==========================================
# VERIFY DATABASE
# ==========================================

cursor.execute(
    "SELECT COUNT(*) FROM analytics.companies;"
)

company_count = cursor.fetchone()[0]

cursor.execute(
    "SELECT COUNT(*) FROM analytics.locations;"
)

location_count = cursor.fetchone()[0]

print("\n========== DATABASE VERIFICATION ==========")
print("Companies in PostgreSQL:", company_count)
print("Locations in PostgreSQL:", location_count)


# ==========================================
# CLOSE CONNECTION
# ==========================================

cursor.close()
connection.close()

print("\nConnection closed.")
print("Dimension loading completed successfully.")