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
# SKILL LIST
# ==============================

skills = [
    "Python",
    "R",
    "SQL",
    "Java",
    "C++",
    "C#",
    "Scala",

    "Power BI",
    "Tableau",
    "Excel",
    "Looker",
    "Qlik",
    "Alteryx",

    "MySQL",
    "PostgreSQL",
    "SQL Server",
    "Oracle",
    "Snowflake",
    "MongoDB",
    "Databricks",

    "AWS",
    "Azure",
    "Google Cloud",

    "ETL",
    "Apache Spark",
    "Hadoop",
    "Airflow",
    "Kafka",
    "Data Warehousing",

    "Machine Learning",
    "Deep Learning",
    "NLP",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn"
]

# ==============================
# INSERT SKILLS
# ==============================

for skill in skills:

    cur.execute(
        """
        INSERT INTO analytics.skills (skill_name)
        VALUES (%s)
        ON CONFLICT (skill_name)
        DO NOTHING;
        """,
        (skill,)
    )

conn.commit()

# ==============================
# VERIFY
# ==============================

cur.execute("""
    SELECT COUNT(*)
    FROM analytics.skills;
""")

count = cur.fetchone()[0]

print("========== SKILL LOAD STATUS ==========")
print("Skills loaded:", count)

# Display skills
cur.execute("""
    SELECT skill_id, skill_name
    FROM analytics.skills
    ORDER BY skill_id;
""")

for skill_id, skill_name in cur.fetchall():
    print(skill_id, "-", skill_name)

cur.close()
conn.close()