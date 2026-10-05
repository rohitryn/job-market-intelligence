import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = "data/processed/ml_salary_dataset.csv"

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

query = """
SELECT *
FROM analytics.ml_salary_dataset
ORDER BY job_id;
"""

df = pd.read_sql(query, conn)

conn.close()

df.to_csv(OUTPUT_FILE, index=False)

print("ML dataset exported successfully.")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {OUTPUT_FILE}")

print("\nColumns:")
print(df.columns.tolist())