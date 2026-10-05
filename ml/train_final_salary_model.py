import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# LOAD DATA
# ============================================================

FILE = "data/processed/ml_salary_dataset_skill_engineered.csv"

df = pd.read_csv(FILE)

print("Dataset shape:", df.shape)


# ============================================================
# TEXT COLUMNS
# ============================================================

df["job_title"] = df["job_title"].fillna("Unknown")
df["skills"] = df["skills"].fillna("Unknown")


# ============================================================
# FEATURES
# ============================================================

categorical_features = [
    "category",
    "company",
    "city",
    "location_type",
    "experience_category",
    "title_seniority",
]

numeric_features = [
    "experience_min",
    "experience_max",
    "experience_mid",
    "experience_range",
    "is_entry_level",
    "experience_missing",
    "title_length",
    "title_word_count",
    "skills_missing",
    "skill_count",
]


# Add engineered skill features
skill_features = [
    col for col in df.columns
    if col.startswith("has_")
]

numeric_features.extend(skill_features)


# ============================================================
# TARGET
# ============================================================

X = df[
    [
        "job_title",
        "skills",
        *categorical_features,
        *numeric_features,
    ]
]

y = df["salary_target"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Train size:", len(X_train))
print("Test size :", len(X_test))


# ============================================================
# PREPROCESSING
# ============================================================

job_title_tfidf = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=150,
            ngram_range=(1, 2),
            min_df=2
        )
    )
])

skills_tfidf = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            min_df=2
        )
    )
])


categorical_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )
])


numeric_pipeline = Pipeline([
    (
        "imputer",
        SimpleImputer(
            strategy="median",
            add_indicator=True
        )
    )
])


preprocessor = ColumnTransformer(
    transformers=[
        (
            "job_title",
            job_title_tfidf,
            "job_title"
        ),
        (
            "skills",
            skills_tfidf,
            "skills"
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        ),
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
    ]
)


# ============================================================
# MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# FULL PIPELINE
# ============================================================

pipeline = Pipeline([
    (
        "preprocessor",
        preprocessor
    ),
    (
        "model",
        model
    )
])


# ============================================================
# TRAIN
# ============================================================

print("\nTraining final Random Forest...")

pipeline.fit(X_train, y_train)


# ============================================================
# PREDICTION
# ============================================================

predictions = pipeline.predict(X_test)


# ============================================================
# EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n========================================")
print("FINAL MODEL PERFORMANCE")
print("========================================")

print(f"MAE  : ₹{mae:,.0f}")
print(f"RMSE : ₹{rmse:,.0f}")
print(f"R²   : {r2:.3f}")


# ============================================================
# BASELINE
# ============================================================

baseline_prediction = np.repeat(
    y_train.median(),
    len(y_test)
)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_prediction
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_prediction
    )
)

baseline_r2 = r2_score(
    y_test,
    baseline_prediction
)


print("\n========================================")
print("MEDIAN BASELINE")
print("========================================")

print(f"MAE  : ₹{baseline_mae:,.0f}")
print(f"RMSE : ₹{baseline_rmse:,.0f}")
print(f"R²   : {baseline_r2:.3f}")


# ============================================================
# IMPROVEMENT
# ============================================================

print("\n========================================")
print("IMPROVEMENT OVER BASELINE")
print("========================================")

print(
    f"MAE improvement : ₹{baseline_mae - mae:,.0f}"
)

print(
    f"RMSE improvement: ₹{baseline_rmse - rmse:,.0f}"
)

print(
    f"R² improvement  : {r2 - baseline_r2:.3f}"
)


print("\nFinal model training complete.")