import json
import glob
import pandas as pd


# ==================================================
# FIND LATEST ADZUNA RAW FILE
# ==================================================

files = sorted(
    glob.glob("data/raw/adzuna_large_*.json")
)

if not files:
    raise FileNotFoundError(
        "No Adzuna raw files found."
    )

input_file = files[-1]

print("Reading:", input_file)


# ==================================================
# LOAD RAW JSON
# ==================================================

with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


print("Raw jobs:", len(jobs))


# ==================================================
# STANDARDIZE
# ==================================================

standardized_jobs = []


for job in jobs:

    company_data = job.get("company") or {}
    location_data = job.get("location") or {}
    category_data = job.get("category") or {}

    standardized_job = {

        "job_id": job.get("id"),

        "job_title": job.get("title"),

        "company": company_data.get(
            "display_name"
        ),

        "location": location_data.get(
            "display_name"
        ),

        "category": category_data.get(
            "label"
        ),

        "salary_min": job.get(
            "salary_min"
        ),

        "salary_max": job.get(
            "salary_max"
        ),

        "salary_is_predicted": job.get(
            "salary_is_predicted"
        ),

        "contract_type": job.get(
            "contract_type"
        ),

        "contract_time": job.get(
            "contract_time"
        ),

        "description": job.get(
            "description"
        ),

        "posting_date": job.get(
            "created"
        ),

        "job_url": job.get(
            "redirect_url"
        ),

        "latitude": job.get(
            "latitude"
        ),

        "longitude": job.get(
            "longitude"
        ),

        "source": "Adzuna",

        "collection_query": job.get(
            "_collection_query"
        ),

        "collection_location": job.get(
            "_collection_location"
        )
    }

    standardized_jobs.append(
        standardized_job
    )


# ==================================================
# CREATE DATAFRAME
# ==================================================

df = pd.DataFrame(
    standardized_jobs
)


# ==================================================
# REMOVE DUPLICATE JOB IDS
# ==================================================

before = len(df)

df = df.drop_duplicates(
    subset=["job_id"]
)

after = len(df)


print(
    "Duplicates removed:",
    before - after
)


# ==================================================
# BASIC CLEANING
# ==================================================

# Remove completely empty job IDs

df = df[
    df["job_id"].notna()
]


# Convert job ID to integer

df["job_id"] = df[
    "job_id"
].astype("int64")


# Remove leading/trailing spaces

text_columns = [
    "job_title",
    "company",
    "location",
    "category",
    "contract_type",
    "contract_time",
    "description",
    "job_url",
    "collection_query",
    "collection_location"
]


for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ==================================================
# SAVE
# ==================================================

output_file = (
    "data/processed/"
    "standardized_adzuna_jobs.csv"
)


df.to_csv(
    output_file,
    index=False
)


# ==================================================
# SUMMARY
# ==================================================

print("\n===================================")
print("STANDARDIZATION COMPLETED")
print("===================================")

print(
    "Final jobs:",
    len(df)
)

print(
    "Columns:",
    len(df.columns)
)

print(
    "Saved to:",
    output_file
)

print("\nDataset shape:")
print(df.shape)

print("\nPreview:")
print(
    df[
        [
            "job_id",
            "job_title",
            "company",
            "location",
            "salary_min",
            "salary_max"
        ]
    ].head()
)