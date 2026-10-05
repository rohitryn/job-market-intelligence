import pandas as pd


JOBS_FILE = "data/processed/master_jobs_cleaned.csv"
SKILLS_FILE = "data/processed/job_skills_extracted.csv"


jobs = pd.read_csv(JOBS_FILE)
skills = pd.read_csv(SKILLS_FILE)


# Get jobs where R was detected
r_jobs = skills[
    skills["skill"] == "R"
]["job_id"]


result = jobs[
    jobs["job_id"].isin(r_jobs)
][
    [
        "job_id",
        "job_title",
        "company",
        "description"
    ]
]


print("Jobs containing detected R skill:", len(result))

print("\n========== SAMPLE R JOBS ==========")

for _, row in result.head(30).iterrows():

    print("\n-----------------------------------")
    print("Title:", row["job_title"])
    print("Company:", row["company"])
    print("Description:")
    print(str(row["description"])[:1000])