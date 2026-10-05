import pandas as pd


INPUT_FILE = "data/processed/master_jobs.csv"
OUTPUT_FILE = "data/processed/master_jobs_cleaned.csv"


# Load master dataset
df = pd.read_csv(INPUT_FILE)

print("Original records:", len(df))


# Convert invalid salary_min values to missing
invalid_min = (
    df["salary_min"].notna()
    & (df["salary_min"] <= 0)
)

print(
    "Invalid salary_min values:",
    invalid_min.sum()
)

df.loc[invalid_min, "salary_min"] = pd.NA


# Convert invalid salary_max values to missing
invalid_max = (
    df["salary_max"].notna()
    & (df["salary_max"] <= 0)
)

print(
    "Invalid salary_max values:",
    invalid_max.sum()
)

df.loc[invalid_max, "salary_max"] = pd.NA


# Validate salary range again
invalid_ranges = (
    df["salary_min"].notna()
    & df["salary_max"].notna()
    & (df["salary_min"] > df["salary_max"])
)

print(
    "Invalid salary ranges after cleaning:",
    invalid_ranges.sum()
)


# Save cleaned dataset
df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n===================================")
print("SALARY CLEANING COMPLETED")
print("===================================")
print("Records:", len(df))
print("Saved to:", OUTPUT_FILE)