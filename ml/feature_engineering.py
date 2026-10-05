import pandas as pd
import numpy as np


# ==========================================================
# LOAD DATA
# ==========================================================

FILE = "data/processed/ml_salary_dataset.csv"

df = pd.read_csv(FILE)

print("Original shape:", df.shape)


# ==========================================================
# EXPERIENCE MIDPOINT
# ==========================================================

df["experience_mid"] = np.where(
    df["experience_min"].notna()
    & df["experience_max"].notna(),

    (
        df["experience_min"]
        + df["experience_max"]
    ) / 2,

    np.nan
)


# ==========================================================
# EXPERIENCE RANGE
# ==========================================================

df["experience_range"] = np.where(
    df["experience_min"].notna()
    & df["experience_max"].notna(),

    df["experience_max"]
    - df["experience_min"],

    np.nan
)


# ==========================================================
# ENTRY-LEVEL INDICATOR
# ==========================================================

df["is_entry_level"] = (
    (
        df["experience_min"].notna()
        & (df["experience_min"] <= 1)
    )
    .astype(int)
)


# ==========================================================
# EXPERIENCE MISSING INDICATOR
# ==========================================================

df["experience_missing"] = (
    df["experience_min"].isna()
    & df["experience_max"].isna()
).astype(int)


# ==========================================================
# EXPERIENCE CATEGORY
# ==========================================================

def experience_category(row):

    if pd.isna(row["experience_min"]):
        return "Unknown"

    if row["experience_min"] <= 1:
        return "Entry Level"

    if row["experience_min"] < 3:
        return "Junior"

    if row["experience_min"] < 5:
        return "Mid Level"

    if row["experience_min"] < 8:
        return "Senior"

    return "Lead/Expert"


df["experience_category"] = df.apply(
    experience_category,
    axis=1
)


# ==========================================================
# VALIDATION
# ==========================================================

print("\nNew features:")

print(
    df[
        [
            "experience_min",
            "experience_max",
            "experience_mid",
            "experience_range",
            "is_entry_level",
            "experience_missing",
            "experience_category"
        ]
    ].head(15)
)


print("\nExperience category counts:")

print(
    df["experience_category"]
    .value_counts(dropna=False)
)


print("\nMissing values:")

print(
    df[
        [
            "experience_mid",
            "experience_range",
            "experience_category"
        ]
    ].isna().sum()
)


# ==========================================================
# SAVE FEATURE-ENGINEERED DATASET
# ==========================================================

OUTPUT_FILE = (
    "data/processed/"
    "ml_salary_dataset_engineered.csv"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nFeature engineering complete.")

print(
    f"Saved to: {OUTPUT_FILE}"
)

print(
    "Final shape:",
    df.shape
)