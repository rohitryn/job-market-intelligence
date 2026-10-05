import pandas as pd


# ==========================================
# LOAD CLEANED JOB DATA
# ==========================================

df = pd.read_csv("data/processed_jobs.csv")

print("Total jobs:", len(df))


# ==========================================
# NORMALIZE COMPANIES
# ==========================================

companies_df = (
    df[["company"]]
    .dropna()
    .drop_duplicates()
    .sort_values("company")
    .reset_index(drop=True)
)

companies_df.insert(
    0,
    "company_id",
    range(1, len(companies_df) + 1)
)

companies_df = companies_df.rename(
    columns={"company": "company_name"}
)

print("\n========== COMPANIES ==========")
print(companies_df.head(20).to_string(index=False))

print("\nUnique companies:", len(companies_df))


# ==========================================
# NORMALIZE LOCATIONS
# ==========================================

locations_df = (
    df[["location"]]
    .dropna()
    .drop_duplicates()
    .sort_values("location")
    .reset_index(drop=True)
)

locations_df.insert(
    0,
    "location_id",
    range(1, len(locations_df) + 1)
)

locations_df = locations_df.rename(
    columns={"location": "location_name"}
)

print("\n========== LOCATIONS ==========")
print(locations_df.head(20).to_string(index=False))

print("\nUnique locations:", len(locations_df))


# ==========================================
# SAVE FILES
# ==========================================

companies_df.to_csv(
    "data/processed/companies.csv",
    index=False
)

locations_df.to_csv(
    "data/processed/locations.csv",
    index=False
)


print("\n========== FILES CREATED ==========")
print("data/processed/companies.csv")
print("data/processed/locations.csv")