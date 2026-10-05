import pandas as pd


# ==================================================
# LOAD STANDARDIZED DATASETS
# ==================================================

adzuna_file = (
    "data/processed/"
    "standardized_adzuna_jobs.csv"
)

greenhouse_file = (
    "data/processed/"
    "standardized_greenhouse_jobs.csv"
)


adzuna = pd.read_csv(
    adzuna_file
)

greenhouse = pd.read_csv(
    greenhouse_file
)


print("Adzuna jobs:", len(adzuna))
print("Greenhouse jobs:", len(greenhouse))


# ==================================================
# COMBINE
# ==================================================

master = pd.concat(
    [
        adzuna,
        greenhouse
    ],
    ignore_index=True
)


print(
    "\nCombined records:",
    len(master)
)


# ==================================================
# SOURCE-AWARE DEDUPLICATION
# ==================================================

# First remove exact duplicate records
master = master.drop_duplicates(
    subset=[
        "source",
        "job_id"
    ]
)


print(
    "After source/job ID deduplication:",
    len(master)
)


# ==================================================
# SAVE MASTER DATASET
# ==================================================

output_file = (
    "data/processed/"
    "master_jobs.csv"
)

master.to_csv(
    output_file,
    index=False
)


# ==================================================
# SUMMARY
# ==================================================

print("\n===================================")
print("MASTER DATASET CREATED")
print("===================================")

print(
    "Total jobs:",
    len(master)
)

print("\nJobs by source:")

print(
    master["source"]
    .value_counts()
)

print(
    "\nSaved to:",
    output_file
)