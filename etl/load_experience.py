import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()


INPUT_FILE = "data/processed/master_jobs_with_experience.csv"


def convert_value(value):
    """
    Convert pandas missing values to PostgreSQL NULL.
    """

    if pd.isna(value):
        return None

    return float(value)


def main():

    print("Loading experience dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Records in CSV: {len(df)}")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    cur = conn.cursor()

    updated = 0

    for _, row in df.iterrows():

        source = row["source"]
        source_job_id = str(row["job_id"])

        experience_min = convert_value(
            row["experience_min"]
        )

        experience_max = convert_value(
            row["experience_max"]
        )

        cur.execute(
            """
            UPDATE analytics.jobs
            SET
                experience_min = %s,
                experience_max = %s
            WHERE source = %s
              AND source_job_id = %s;
            """,
            (
                experience_min,
                experience_max,
                source,
                source_job_id
            )
        )

        updated += cur.rowcount

    conn.commit()

    print()
    print("========== EXPERIENCE LOAD ==========")

    print(f"CSV records: {len(df)}")
    print(f"Database rows updated: {updated}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()