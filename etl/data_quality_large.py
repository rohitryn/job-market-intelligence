import pandas as pd


# ==================================================
# LOAD STANDARDIZED DATA
# ==================================================

file_path = (
    "data/processed/"
    "master_jobs_cleaned.csv"
)

df = pd.read_csv(file_path)

print("\n===================================")
print("DATA QUALITY REPORT")
print("===================================")


# ==================================================
# BASIC INFORMATION
# ==================================================

print("\n========== DATASET OVERVIEW ==========")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


# ==================================================
# DATA TYPES
# ==================================================

print("\n========== DATA TYPES ==========")

print(df.dtypes)


# ==================================================
# MISSING VALUES
# ==================================================

print("\n========== MISSING VALUES ==========")

missing = df.isnull().sum()

missing_percentage = (
    df.isnull().sum()
    / len(df)
    * 100
)

quality_table = pd.DataFrame({
    "missing_count": missing,
    "missing_percentage": missing_percentage.round(2)
})

print(
    quality_table
    .sort_values(
        "missing_percentage",
        ascending=False
    )
)


# ==================================================
# DUPLICATE JOB IDs
# ==================================================

print("\n========== DUPLICATE JOB IDs ==========")

duplicates = (
    df["job_id"]
    .duplicated()
    .sum()
)

print(
    "Duplicate job IDs:",
    duplicates
)


# ==================================================
# SALARY ANALYSIS
# ==================================================

print("\n========== SALARY ANALYSIS ==========")

salary_available = (
    df["salary_min"]
    .notna()
    .sum()
)

salary_missing = (
    df["salary_min"]
    .isna()
    .sum()
)

print(
    "Jobs with salary:",
    salary_available
)

print(
    "Jobs without salary:",
    salary_missing
)

print(
    "Salary availability:",
    round(
        salary_available / len(df) * 100,
        2
    ),
    "%"
)


# ==================================================
# PREDICTED VS NON-PREDICTED SALARY
# ==================================================

print(
    "\n========== SALARY TYPE =========="
)

print(
    df[
        "salary_is_predicted"
    ].value_counts(
        dropna=False
    )
)


# ==================================================
# JOB TITLE DISTRIBUTION
# ==================================================

print(
    "\n========== TOP JOB TITLES =========="
)

print(
    df[
        "job_title"
    ]
    .value_counts()
    .head(20)
)


# ==================================================
# COMPANY DISTRIBUTION
# ==================================================

print(
    "\n========== TOP COMPANIES =========="
)

print(
    df[
        "company"
    ]
    .value_counts()
    .head(20)
)


# ==================================================
# LOCATION DISTRIBUTION
# ==================================================

print(
    "\n========== TOP LOCATIONS =========="
)

print(
    df[
        "location"
    ]
    .value_counts()
    .head(20)
)


# ==================================================
# CATEGORY DISTRIBUTION
# ==================================================

print(
    "\n========== JOB CATEGORIES =========="
)

print(
    df[
        "category"
    ]
    .value_counts()
    .head(20)
)


# ==================================================
# CONTRACT TYPE
# ==================================================

print(
    "\n========== CONTRACT TYPE =========="
)

print(
    df[
        "contract_type"
    ]
    .value_counts(
        dropna=False
    )
)


# ==================================================
# CONTRACT TIME
# ==================================================

print(
    "\n========== CONTRACT TIME =========="
)

print(
    df[
        "contract_time"
    ]
    .value_counts(
        dropna=False
    )
)


# ==================================================
# DESCRIPTION QUALITY
# ==================================================

print(
    "\n========== DESCRIPTION QUALITY =========="
)

description_missing = (
    df["description"]
    .isna()
    .sum()
)

description_empty = (
    df["description"]
    .fillna("")
    .str.strip()
    .eq("")
    .sum()
)

print(
    "Missing descriptions:",
    description_missing
)

print(
    "Empty descriptions:",
    description_empty
)


# ==================================================
# SALARY RANGE VALIDATION
# ==================================================

print(
    "\n========== SALARY VALIDATION =========="
)

invalid_salary = df[
    (
        df["salary_min"].notna()
    )
    &
    (
        df["salary_max"].notna()
    )
    &
    (
        df["salary_min"]
        >
        df["salary_max"]
    )
]

print(
    "Invalid salary ranges:",
    len(invalid_salary)
)


# ==================================================
# FINAL SUMMARY
# ==================================================

print(
    "\n==================================="
)

print(
    "DATA QUALITY CHECK COMPLETED"
)

print(
    "==================================="
)
# ==================================================
# SALARY VALIDATION
# ==================================================

print("\n========== SALARY VALIDATION ==========")

salary_data = df[
    df["salary_min"].notna() |
    df["salary_max"].notna()
].copy()

print("Salary records:", len(salary_data))


# Missing one side of salary
missing_min = salary_data["salary_min"].isna().sum()
missing_max = salary_data["salary_max"].isna().sum()

print("Missing salary_min:", missing_min)
print("Missing salary_max:", missing_max)


# Invalid negative / zero salaries
invalid_min = (
    salary_data["salary_min"].notna() &
    (salary_data["salary_min"] <= 0)
).sum()

invalid_max = (
    salary_data["salary_max"].notna() &
    (salary_data["salary_max"] <= 0)
).sum()

print("Invalid salary_min:", invalid_min)
print("Invalid salary_max:", invalid_max)


# min greater than max
invalid_range = (
    salary_data["salary_min"].notna() &
    salary_data["salary_max"].notna() &
    (salary_data["salary_min"] > salary_data["salary_max"])
).sum()

print("salary_min > salary_max:", invalid_range)


# Salary statistics
print("\nSalary statistics:")

print(
    salary_data[
        ["salary_min", "salary_max"]
    ].describe()
)