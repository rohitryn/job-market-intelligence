import json
import glob
import hashlib
import pandas as pd


# Find all raw JSON files
files = glob.glob("data/raw/*.json")

print("Raw files found:", len(files))

all_jobs = []


for file in files:

    print("\nReading:", file)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # -----------------------------
    # Detect source
    # -----------------------------

    if "greenhouse" in file.lower():

        source = "Greenhouse"

        jobs = data

        for job in jobs:

            cleaned_job = {
                "job_id": None,
                "job_title": job.get("job_title"),
                "company": None,
                "location": job.get("location"),
                "category": None,
                "salary_min": None,
                "salary_max": None,
                "description": job.get("description"),
                "posting_date": None,
                "job_url": job.get("job_url"),
                "latitude": None,
                "longitude": None,
                "source": source,
                "scraped_at": job.get("scraped_at")
            }

            all_jobs.append(cleaned_job)

    else:

        source = "Adzuna"

        # Adzuna files may contain either
        # a list or {"results": [...]}

        if isinstance(data, dict):
            jobs = data.get("results", [])
        else:
            jobs = data

        for job in jobs:

            cleaned_job = {
                "job_id": job.get("id"),
                "job_title": job.get("title"),
                "company": job.get("company", {}).get("display_name"),
                "location": job.get("location", {}).get("display_name"),
                "category": job.get("category", {}).get("label"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "description": job.get("description"),
                "posting_date": job.get("created"),
                "job_url": job.get("redirect_url"),
                "latitude": job.get("latitude"),
                "longitude": job.get("longitude"),
                "source": source,
                "scraped_at": None
            }

            all_jobs.append(cleaned_job)


print("\nTotal records collected:", len(all_jobs))


# -----------------------------------
# Convert to DataFrame
# -----------------------------------

df = pd.DataFrame(all_jobs)


# -----------------------------------
# Create unique job IDs for scraped
# jobs that don't have an ID
# -----------------------------------

# -----------------------------------
# Create stable numeric IDs for
# scraped jobs
# -----------------------------------

for index, row in df.iterrows():

    if pd.isna(row["job_id"]):

        unique_string = (
            row["source"] + "|" + row["job_url"]
        )

        hash_value = hashlib.md5(
            unique_string.encode("utf-8")
        ).hexdigest()

        numeric_id = int(
            hash_value[:15],
            16
        )

        # Keep ID within PostgreSQL BIGINT range
        numeric_id = numeric_id % 900000000000000000

        df.at[index, "job_id"] = numeric_id


# -----------------------------------
# Remove duplicate job IDs
# -----------------------------------

df = df.drop_duplicates(
    subset=["job_id"]
)


print("\nUnique jobs:", len(df))


# -----------------------------------
# Show source distribution
# -----------------------------------

print("\n========== SOURCE DISTRIBUTION ==========")

print(
    df["source"].value_counts()
)


# -----------------------------------
# Dataset preview
# -----------------------------------

print("\n========== DATASET PREVIEW ==========")

print(
    df[
        [
            "job_id",
            "job_title",
            "company",
            "location",
            "source"
        ]
    ].head(10)
)


# -----------------------------------
# Save processed dataset
# -----------------------------------

output_file = "data/processed_jobs.csv"

df.to_csv(
    output_file,
    index=False
)

print("\nProcessed data saved to:", output_file)