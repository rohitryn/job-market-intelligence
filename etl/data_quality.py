import pandas as pd

# Load processed dataset
df = pd.read_csv("data/processed_jobs.csv")

print("========== DATASET OVERVIEW ==========")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


print("\n========== DATA TYPES ==========")

print(df.dtypes)


print("\n========== MISSING VALUES ==========")

missing = df.isnull().sum()

print(missing)


print("\n========== MISSING VALUE % ==========")

missing_percentage = (df.isnull().sum() / len(df)) * 100

print(missing_percentage.round(2))


print("\n========== DUPLICATE JOB IDs ==========")

duplicates = df["job_id"].duplicated().sum()

print("Duplicate job IDs:", duplicates)


print("\n========== SALARY AVAILABILITY ==========")

salary_available = df["salary_min"].notnull().sum()

salary_missing = df["salary_min"].isnull().sum()

print("Jobs with salary:", salary_available)
print("Jobs without salary:", salary_missing)


print("\n========== JOB TITLE DISTRIBUTION ==========")

print(df["job_title"].value_counts().head(10))


print("\n========== TOP COMPANIES ==========")

print(df["company"].value_counts().head(10))


print("\n========== TOP LOCATIONS ==========")

print(df["location"].value_counts().head(10))