import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD EXPERIENCE-ENGINEERED DATASET
# ============================================================

FILE = "data/processed/ml_salary_dataset_engineered.csv"

df = pd.read_csv(FILE)

print("Original shape:", df.shape)


# ============================================================
# 2. CLEAN JOB TITLES
# ============================================================

df["job_title"] = df["job_title"].fillna("Unknown").astype(str)

title = df["job_title"].str.lower()


# ============================================================
# 3. TITLE LENGTH FEATURES
# ============================================================

df["title_length"] = df["job_title"].str.len()

df["title_word_count"] = (
    df["job_title"]
    .str.split()
    .str.len()
)


# ============================================================
# 4. SENIORITY FEATURES
# ============================================================

patterns = {
    "is_intern": r"\bintern(?:ship)?\b",
    "is_junior": r"\b(?:junior|jr\.?)\b",
    "is_senior": r"\b(?:senior|sr\.?)\b",
    "is_lead": r"\b(?:lead|team lead)\b",
    "is_manager": r"\b(?:manager|mgr\.?)\b",
    "is_director": r"\bdirector\b",
    "is_principal": r"\bprincipal\b",
    "is_head": r"\bhead\b",
    "is_chief": r"\bchief\b",
    "is_vp": r"\b(?:vp|vice president)\b",
}

for feature, pattern in patterns.items():
    df[feature] = title.str.contains(
        pattern,
        regex=True,
        na=False
    ).astype(int)


# ============================================================
# 5. COMBINED SENIORITY CATEGORY
# ============================================================

def detect_seniority(row):

    # More senior titles take precedence
    if row["is_chief"]:
        return "Chief"

    if row["is_vp"]:
        return "VP"

    if row["is_director"]:
        return "Director"

    if row["is_head"]:
        return "Head"

    if row["is_principal"]:
        return "Principal"

    if row["is_manager"]:
        return "Manager"

    if row["is_lead"]:
        return "Lead"

    if row["is_senior"]:
        return "Senior"

    if row["is_junior"]:
        return "Junior"

    if row["is_intern"]:
        return "Intern"

    return "Unspecified"


df["title_seniority"] = df.apply(
    detect_seniority,
    axis=1
)


# ============================================================
# 6. INSPECT FEATURES
# ============================================================

new_features = [
    "title_length",
    "title_word_count",
    "is_intern",
    "is_junior",
    "is_senior",
    "is_lead",
    "is_manager",
    "is_director",
    "is_principal",
    "is_head",
    "is_chief",
    "is_vp",
    "title_seniority",
]

print("\nSample title features:")
print(
    df[
        ["job_title"] + new_features
    ].head(20).to_string(index=False)
)


print("\nSeniority category counts:")
print(
    df["title_seniority"]
    .value_counts(dropna=False)
)


print("\nSeniority indicator counts:")
for feature in patterns:
    print(
        f"{feature}: {df[feature].sum()}"
    )


# ============================================================
# 7. SAVE DATASET
# ============================================================

OUTPUT_FILE = (
    "data/processed/"
    "ml_salary_dataset_title_engineered.csv"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nTitle feature engineering complete.")
print("Saved to:", OUTPUT_FILE)
print("Final shape:", df.shape)