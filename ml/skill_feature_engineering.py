import pandas as pd

# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = "data/processed/ml_salary_dataset_title_engineered.csv"
OUTPUT_FILE = "data/processed/ml_salary_dataset_skill_engineered.csv"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("Original shape:", df.shape)


# ============================================================
# SKILL MISSING FLAG
# ============================================================

df["skills_missing"] = (
    df["skills"].isna()
    | df["skills"].astype(str).str.strip().eq("")
).astype(int)


# ============================================================
# PARSE SKILLS
# ============================================================

def parse_skills(value):

    if pd.isna(value) or not str(value).strip():
        return set()

    return {
        skill.strip().lower()
        for skill in str(value).split(",")
        if skill.strip()
    }


parsed_skills = df["skills"].apply(parse_skills)


# ============================================================
# SKILL COUNT
# ============================================================

df["skill_count"] = parsed_skills.apply(len)


# ============================================================
# INDIVIDUAL SKILL FEATURES
# ============================================================

skill_features = {
    "has_python": "python",
    "has_sql": "sql",
    "has_aws": "aws",
    "has_excel": "excel",
    "has_azure": "azure",
    "has_google_cloud": "google cloud",
    "has_machine_learning": "machine learning",
    "has_etl": "etl",
    "has_power_bi": "power bi",
    "has_databricks": "databricks",
    "has_java": "java",
    "has_spark": "apache spark",
    "has_oracle": "oracle",
    "has_tableau": "tableau",
    "has_data_warehousing": "data warehousing",
    "has_snowflake": "snowflake",
    "has_kafka": "kafka",
    "has_nlp": "nlp",
    "has_airflow": "airflow",
    "has_pytorch": "pytorch",
    "has_postgresql": "postgresql",
    "has_scikit_learn": "scikit-learn",
    "has_deep_learning": "deep learning",
    "has_hadoop": "hadoop",
    "has_scala": "scala",
    "has_r": "r",
    "has_tensorflow": "tensorflow",
    "has_sql_server": "sql server",
    "has_mysql": "mysql",
    "has_mongodb": "mongodb",
    "has_csharp": "c#",
    "has_looker": "looker",
    "has_qlik": "qlik",
    "has_alteryx": "alteryx",
}


for feature_name, skill_name in skill_features.items():

    df[feature_name] = parsed_skills.apply(
        lambda skills: int(skill_name in skills)
    )


# ============================================================
# BROAD SKILL CATEGORIES
# ============================================================

category_skills = {

    "has_cloud_skill": {
        "aws",
        "azure",
        "google cloud",
    },

    "has_bi_skill": {
        "power bi",
        "tableau",
        "looker",
        "qlik",
        "alteryx",
    },

    "has_ml_skill": {
        "machine learning",
        "deep learning",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "nlp",
    },

    "has_database_skill": {
        "sql",
        "oracle",
        "postgresql",
        "sql server",
        "mysql",
        "mongodb",
        "snowflake",
    },

    "has_data_engineering_skill": {
        "etl",
        "databricks",
        "apache spark",
        "kafka",
        "airflow",
        "hadoop",
        "data warehousing",
    },
}


for feature_name, skills_set in category_skills.items():

    df[feature_name] = parsed_skills.apply(
        lambda skills: int(bool(skills.intersection(skills_set)))
    )


# ============================================================
# VALIDATION
# ============================================================

print("\nSkill feature sample:")
print(
    df[
        [
            "job_title",
            "skills",
            "skills_missing",
            "skill_count",
            "has_python",
            "has_sql",
            "has_power_bi",
            "has_machine_learning",
        ]
    ].head(10)
)


print("\nSkill counts:")
for feature_name in skill_features:
    print(f"{feature_name}: {df[feature_name].sum()}")


print("\nSkill category counts:")
for feature_name in category_skills:
    print(f"{feature_name}: {df[feature_name].sum()}")


print("\nMissing skill count:")
print(df["skills_missing"].value_counts())


# ============================================================
# SAVE
# ============================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nSkill feature engineering complete.")
print("Saved to:", OUTPUT_FILE)
print("Final shape:", df.shape)