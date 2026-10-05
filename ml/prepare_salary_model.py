import pandas as pd

FILE = "data/processed/ml_salary_dataset.csv"

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(FILE)

print("Dataset shape:", df.shape)

# ==========================================================
# TARGET
# ==========================================================

y = df["salary_target"]

# ==========================================================
# FEATURES
# ==========================================================

X = df[
    [
        "job_title",
        "category",
        "company",
        "city",
        "location_type",
        "experience_min",
        "experience_max",
        "skills"
    ]
].copy()

# ==========================================================
# HANDLE TEXT MISSING VALUES
# ==========================================================

text_columns = [
    "job_title",
    "category",
    "company",
    "city",
    "location_type",
    "skills"
]

for column in text_columns:
    X[column] = X[column].fillna("Unknown")

# ==========================================================
# EXPERIENCE MISSING INDICATORS
# ==========================================================

X["experience_min_missing"] = X["experience_min"].isna().astype(int)
X["experience_max_missing"] = X["experience_max"].isna().astype(int)

print("\nMissing-value indicators:")
print(
    X[
        [
            "experience_min_missing",
            "experience_max_missing"
        ]
    ].sum()
)

# ==========================================================
# DISPLAY
# ==========================================================

print("\nFeatures:")
print(X.head())

print("\nTarget:")
print(y.head())

print("\nFeature columns:")
print(X.columns.tolist())