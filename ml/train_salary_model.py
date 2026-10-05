import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================================
# LOAD DATA
# ==========================================================

FILE = "data/processed/ml_salary_dataset.csv"

df = pd.read_csv(FILE)

print("Dataset shape:", df.shape)


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
# TARGET
# ==========================================================

y = df["salary_target"]


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

X["experience_min_missing"] = (
    X["experience_min"].isna().astype(int)
)

X["experience_max_missing"] = (
    X["experience_max"].isna().astype(int)
)


# ==========================================================
# TRAIN / TEST SPLIT
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================================
# LOG TRANSFORM TARGET
# ==========================================================

y_train_log = np.log1p(y_train)


print("\nOriginal target statistics:")
print(f"Minimum salary: ₹{y.min():,.0f}")
print(f"Maximum salary: ₹{y.max():,.0f}")
print(f"Median salary : ₹{y.median():,.0f}")

print("\nLog-transformed target:")
print(
    f"Minimum: {y_train_log.min():.3f}"
)

print(
    f"Maximum: {y_train_log.max():.3f}"
)


# ==========================================================
# FEATURE GROUPS
# ==========================================================

categorical_features = [
    "category",
    "company",
    "city",
    "location_type"
]

numeric_features = [
    "experience_min",
    "experience_max",
    "experience_min_missing",
    "experience_max_missing"
]


# ==========================================================
# NUMERIC PIPELINE
# ==========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


# ==========================================================
# CATEGORICAL PIPELINE
# ==========================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# ==========================================================
# JOB TITLE TF-IDF
# ==========================================================

job_title_pipeline = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                min_df=2,
                lowercase=True
            )
        )
    ]
)


# ==========================================================
# SKILLS TF-IDF
# ==========================================================

skills_pipeline = Pipeline(
    steps=[
        (
            "tfidf",
            TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                min_df=2,
                lowercase=True
            )
        )
    ]
)


# ==========================================================
# PREPROCESSOR
# ==========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        ),
        (
            "job_title",
            job_title_pipeline,
            "job_title"
        ),
        (
            "skills",
            skills_pipeline,
            "skills"
        )
    ]
)


# ==========================================================
# RANDOM FOREST
# ==========================================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)


# ==========================================================
# COMPLETE PIPELINE
# ==========================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# ==========================================================
# TRAIN
# ==========================================================

print("\nTraining log-target Random Forest...")

pipeline.fit(
    X_train,
    y_train_log
)

print("Training complete.")


# ==========================================================
# PREDICT LOG SALARY
# ==========================================================

y_pred_log = pipeline.predict(
    X_test
)


# ==========================================================
# CONVERT BACK TO RUPEES
# ==========================================================

y_pred = np.expm1(
    y_pred_log
)


# ==========================================================
# EVALUATION
# ==========================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


# ==========================================================
# RESULTS
# ==========================================================

print("\n==============================")
print("LOG-TARGET RANDOM FOREST")
print("==============================")

print(f"MAE : ₹{mae:,.0f}")
print(f"RMSE: ₹{rmse:,.0f}")
print(f"R²  : {r2:.3f}")


# ==========================================================
# SAMPLE PREDICTIONS
# ==========================================================

results = X_test.copy()

results["actual_salary"] = y_test

results["predicted_salary"] = y_pred

results["error"] = (
    results["actual_salary"]
    - results["predicted_salary"]
)

print("\nSample predictions:")

print(
    results[
        [
            "job_title",
            "city",
            "actual_salary",
            "predicted_salary",
            "error"
        ]
    ]
    .head(10)
    .to_string(index=False)
)