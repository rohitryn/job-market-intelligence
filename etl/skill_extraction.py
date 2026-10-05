import pandas as pd
import re


INPUT_FILE = "data/processed/master_jobs_cleaned.csv"
OUTPUT_FILE = "data/processed/job_skills_extracted.csv"


# ==================================================
# SKILL DICTIONARY
# ==================================================

SKILLS = {
    "Python": [
        r"\bpython\b"
    ],

    "R": [
        r"\br\s+programming\b",
        r"\br\s+language\b",
        r"\br\s+studio\b",
        r"\br\s*/\s*python\b",
        r"\bpython\s*/\s*r\b",
        r"\br\s*,\s*(?:sql|python|excel|sas|tableau|power\s*bi)\b",
        r"\b(?:sql|python|excel|sas|tableau|power\s*bi)\s*,\s*r\b",
        r"\br\s+and\s+(?:python|sql|sas)\b",
    ],

    "SQL": [
        r"\bsql\b"
    ],

    "Java": [
        r"\bjava\b"
    ],

    "C++": [
        r"\bc\+\+\b"
    ],

    "C#": [
        r"(?<![a-zA-Z])c#(?![a-zA-Z])"
    ],

    "Scala": [
        r"\bscala\b"
    ],

    "Power BI": [
        r"\bpower\s*bi\b"
    ],

    "Tableau": [
        r"\btableau\b"
    ],

    "Excel": [
        r"\bexcel\b",
        r"\bmicrosoft\s+excel\b"
    ],

    "Looker": [
        r"\blooker\b"
    ],

    "Qlik": [
        r"\bqlik\b"
    ],

    "Alteryx": [
        r"\balteryx\b"
    ],

    "MySQL": [
        r"\bmysql\b"
    ],

    "PostgreSQL": [
        r"\bpostgresql\b",
        r"\bpostgres\b"
    ],

    "SQL Server": [
        r"\bsql\s+server\b",
        r"\bmicrosoft\s+sql\s+server\b"
    ],

    "Oracle": [
        r"\boracle\b"
    ],

    "Snowflake": [
        r"\bsnowflake\b"
    ],

    "MongoDB": [
        r"\bmongodb\b",
        r"\bmongo\s*db\b"
    ],

    "Databricks": [
        r"\bdatabricks\b"
    ],

    "AWS": [
        r"\baws\b",
        r"\bamazon\s+web\s+services\b"
    ],

    "Azure": [
        r"\bazure\b",
        r"\bmicrosoft\s+azure\b"
    ],

    "Google Cloud": [
        r"\bgoogle\s+cloud\b",
        r"\bgcp\b"
    ],

    "ETL": [
        r"\betl\b",
        r"\bextract[\s-]*transform[\s-]*load\b"
    ],

    "Apache Spark": [
        r"\bapache\s+spark\b",
        r"\bspark\b"
    ],

    "Hadoop": [
        r"\bhadoop\b"
    ],

    "Airflow": [
        r"\bairflow\b",
        r"\bapache\s+airflow\b"
    ],

    "Kafka": [
        r"\bkafka\b",
        r"\bapache\s+kafka\b"
    ],

    "Data Warehousing": [
        r"\bdata\s+warehouse\b",
        r"\bdata\s+warehousing\b"
    ],

    "Machine Learning": [
        r"\bmachine\s+learning\b"
    ],

    "Deep Learning": [
        r"\bdeep\s+learning\b"
    ],

    "NLP": [
        r"\bnlp\b",
        r"\bnatural\s+language\s+processing\b"
    ],

    "TensorFlow": [
        r"\btensorflow\b"
    ],

    "PyTorch": [
        r"\bpytorch\b"
    ],

    "Scikit-learn": [
        r"\bscikit[\s-]*learn\b",
        r"\bsklearn\b"
    ],
}


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(INPUT_FILE)

print("Total jobs:", len(df))


# ==================================================
# SKILL EXTRACTION
# ==================================================

records = []

for _, row in df.iterrows():

    job_id = row["job_id"]

    title = str(row["job_title"])
    description = str(row["description"])

    text = f"{title} {description}"

    # Case-insensitive matching
    text = text.lower()

    found_skills = set()

    for skill, patterns in SKILLS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                found_skills.add(skill)
                break

    for skill in found_skills:

        records.append({
            "job_id": job_id,
            "skill": skill
        })


# ==================================================
# CREATE DATAFRAME
# ==================================================

skills_df = pd.DataFrame(records)


# Remove accidental duplicates
skills_df = skills_df.drop_duplicates(
    subset=["job_id", "skill"]
)


# ==================================================
# SAVE
# ==================================================

skills_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==================================================
# RESULTS
# ==================================================

print("\n===================================")
print("SKILL EXTRACTION COMPLETED")
print("===================================")

print(
    "Jobs processed:",
    len(df)
)

print(
    "Unique skills detected:",
    skills_df["skill"].nunique()
)

print(
    "Job-skill relationships:",
    len(skills_df)
)

print(
    "Jobs with at least one skill:",
    skills_df["job_id"].nunique()
)

print(
    "Jobs with no detected skills:",
    len(df) - skills_df["job_id"].nunique()
)


# ==================================================
# TOP SKILLS
# ==================================================

print("\n========== TOP SKILLS ==========")

print(
    skills_df["skill"]
    .value_counts()
    .head(20)
)


print(
    "\nSaved to:",
    OUTPUT_FILE
)