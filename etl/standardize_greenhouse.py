import json
import glob
import pandas as pd


# ==================================================
# FIND LATEST GREENHOUSE RAW FILE
# ==================================================

files = sorted(
    glob.glob("data/raw/greenhouse_raw_*.json")
)

if not files:
    raise FileNotFoundError(
        "No Greenhouse raw files found."
    )

input_file = files[-1]

print("Reading:", input_file)


# ==================================================
# LOAD RAW DATA
# ==================================================

with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


print("Raw Greenhouse jobs:", len(jobs))


# ==================================================
# STANDARDIZE
# ==================================================

standardized_jobs = []


for job in jobs:

    # Greenhouse location
    location = job.get("location")

    # Greenhouse company/board token
    company = job.get("source_company")

    # Departments
    departments = job.get("departments")

    if departments:

        department_names = [
            d.get("name")
            for d in departments
            if isinstance(d, dict)
        ]

        department = ", ".join(
            x for x in department_names
            if x
        )

    else:
        department = None


    standardized_job = {

        # Greenhouse source ID
        "job_id": job.get(
            "source_job_id"
        ),

        "job_title": job.get(
            "job_title"
        ),

        "company": company,

        "location": location,

        "category": department,

        # Greenhouse usually doesn't
        # provide salary through this endpoint
        "salary_min": None,

        "salary_max": None,

        "salary_is_predicted": None,

        "contract_type": None,

        "contract_time": None,

        "description": job.get(
            "content"
        ),

        "posting_date": job.get(
            "updated_at"
        ),

        "job_url": job.get(
            "absolute_url"
        ),

        "latitude": None,

        "longitude": None,

        "source": "Greenhouse",

        "collection_query": None,

        "collection_location": None
    }

    standardized_jobs.append(
        standardized_job
    )


# ==================================================
# DATAFRAME
# ==================================================

df = pd.DataFrame(
    standardized_jobs
)


# ==================================================
# REMOVE DUPLICATES
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
# REMOVE MISSING JOB IDS
# ==================================================

df = df[
    df["job_id"].notna()
]


# ==================================================
# CLEAN TEXT
# ==================================================

text_columns = [
    "job_title",
    "company",
    "location",
    "category",
    "contract_type",
    "contract_time",
    "description",
    "job_url"
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
    "standardized_greenhouse_jobs.csv"
)

df.to_csv(
    output_file,
    index=False
)


# ==================================================
# SUMMARY
# ==================================================

print("\n===================================")
print("GREENHOUSE STANDARDIZATION COMPLETE")
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

print("\nPreview:")

print(
    df[
        [
            "job_id",
            "job_title",
            "company",
            "location",
            "source"
        ]
    ].head()
)