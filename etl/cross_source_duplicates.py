import pandas as pd


# Load master dataset
df = pd.read_csv(
    "data/processed/master_jobs.csv"
)


print("Total records:", len(df))


# ==================================================
# EXACT URL DUPLICATES
# ==================================================

print("\n========== URL DUPLICATES ==========")

url_duplicates = (
    df["job_url"]
    .duplicated(keep=False)
)

print(
    "Records sharing the same URL:",
    url_duplicates.sum()
)


# ==================================================
# TITLE + COMPANY DUPLICATES
# ==================================================

print(
    "\n========== TITLE + COMPANY DUPLICATES =========="
)

title_company_duplicates = (
    df[
        ["job_title", "company"]
    ]
    .duplicated(
        keep=False
    )
)

print(
    "Potential duplicates:",
    title_company_duplicates.sum()
)


# ==================================================
# SHOW POTENTIAL DUPLICATES
# ==================================================

duplicates = df[
    title_company_duplicates
].sort_values(
    ["job_title", "company"]
)


print(
    "\nPotential duplicate examples:"
)

print(
    duplicates[
        [
            "job_title",
            "company",
            "location",
            "source",
            "job_url"
        ]
    ].head(30)
)


# ==================================================
# CROSS-SOURCE DUPLICATES ONLY
# ==================================================

print(
    "\n========== CROSS-SOURCE DUPLICATES =========="
)

grouped = (
    df
    .groupby(
        [
            "job_title",
            "company",
            "location"
        ],
        dropna=False
    )["source"]
    .nunique()
)

cross_source_keys = grouped[
    grouped > 1
].index


cross_source_duplicates = df[
    df.set_index(
        [
            "job_title",
            "company",
            "location"
        ]
    ).index.isin(
        cross_source_keys
    )
]


print(
    "Records appearing across multiple sources:",
    len(cross_source_duplicates)
)


print(
    "\nCross-source examples:"
)

print(
    cross_source_duplicates[
        [
            "job_title",
            "company",
            "location",
            "source"
        ]
    ].head(30)
)