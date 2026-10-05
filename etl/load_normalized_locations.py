import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==================================================
# LOAD NORMALIZED LOCATION DATA
# ==================================================

input_file = "data/processed/normalized_locations.csv"

df = pd.read_csv(input_file)

print("Locations loaded from CSV:", len(df))


# ==================================================
# CONNECT TO POSTGRESQL
# ==================================================

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()


# ==================================================
# UPDATE EXISTING LOCATION RECORDS
# ==================================================

update_sql = """
UPDATE analytics.locations
SET
    location_type = %s,
    city_normalized = %s,
    country_normalized = %s
WHERE location_id = %s;
"""


updated = 0

try:

    for _, row in df.iterrows():

        city = None if pd.isna(row["city_normalized"]) else row["city_normalized"]
        country = None if pd.isna(row["country_normalized"]) else row["country_normalized"]
        location_type = None if pd.isna(row["location_type"]) else row["location_type"]

        cursor.execute(
            update_sql,
            (
                location_type,
                city,
                country,
                int(row["location_id"])
            )
        )

        updated += cursor.rowcount

    conn.commit()

    print("Locations updated:", updated)

except Exception as e:

    conn.rollback()
    print("Error:", e)
    raise

finally:

    cursor.close()
    conn.close()


print("Location normalization loaded successfully.")