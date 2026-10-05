import pandas as pd


FILE = "data/processed/master_jobs.csv"

df = pd.read_csv(FILE)


invalid = df[
    (df["salary_min"].notna()) &
    (df["salary_min"] <= 0)
].copy()


print("Invalid salary records:", len(invalid))

print("\n========== INVALID SALARY RECORDS ==========")

print(
    invalid[
        [
            "job_id",
            "job_title",
            "company",
            "location",
            "salary_min",
            "salary_max",
            "salary_is_predicted",
            "source"
        ]
    ].to_string(index=False)
)