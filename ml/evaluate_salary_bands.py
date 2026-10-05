import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# 1. LOAD DATA
# ============================================================

FILE = "data/processed/ml_salary_dataset.csv"

df = pd.read_csv(FILE)

print("Dataset shape:", df.shape)


# ============================================================
# 2. FEATURES AND TARGET
# ============================================================

X = df[
    [
        "job_title",
        "category",
        "company",
        "city",
        "location_type",
        "skills",
        "experience_min",
        "experience_max"
    ]
]

y = df["salary_target"]


# ============================================================
# 3. HANDLE TEXT MISSING VALUES
# ============================================================

text_columns = [
    "job_title",
    "category",
    "company",
    "city",
    "location_type",
    "skills"
]

X = X.copy()

for col in text_columns:
    X[col] = X[col].fillna("Unknown")


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTrain size:", len(X_train))
print("Test size :", len(X_test))


# ============================================================
# 5. FEATURES
# ============================================================

categorical_features = [
    "category",
    "company",
    "city",
    "location_type"
]

numeric_features = [
    "experience_min",
    "experience_max"
]

# Add missing-value indicators
X_train = X_train.copy()
X_test = X_test.copy()

for col in numeric_features:

    missing_col = col + "_missing"

    X_train[missing_col] = X_train[col].isna().astype(int)
    X_test[missing_col] = X_test[col].isna().astype(int)

numeric_features_extended = numeric_features + [
    "experience_min_missing",
    "experience_max_missing"
]


# ============================================================
# 6. PREPROCESSING
# ============================================================

categorical_pipeline = Pipeline(
    steps=[
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
    ]
)

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[

        (
            "categorical",
            categorical_pipeline,
            categorical_features
        ),

        (
            "numeric",
            numeric_pipeline,
            numeric_features_extended
        ),

        (
            "job_title",
            TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2)
            ),
            "job_title"
        ),

        (
            "skills",
            TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2)
            ),
            "skills"
        )
    ]
)


# ============================================================
# 7. RANDOM FOREST
# ============================================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 8. TRAIN MODEL
# ============================================================

print("\nTraining Random Forest...")

X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

print(
    "Transformed train shape:",
    X_train_transformed.shape
)

model.fit(
    X_train_transformed,
    y_train
)


# ============================================================
# 9. PREDICTIONS
# ============================================================

predictions = model.predict(X_test_transformed)


# ============================================================
# 10. OVERALL PERFORMANCE
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

print("\nOverall Model Performance")
print("--------------------------------")
print(f"MAE  : ₹{mae:,.0f}")
print(f"RMSE : ₹{rmse:,.0f}")


# ============================================================
# 11. CREATE RESULTS DATAFRAME
# ============================================================

results = pd.DataFrame({

    "actual_salary": y_test.values,

    "predicted_salary": predictions

})

results["absolute_error"] = (
    results["actual_salary"]
    - results["predicted_salary"]
).abs()


# ============================================================
# 12. CREATE SALARY BANDS
# ============================================================

bins = [
    0,
    500000,
    1000000,
    1500000,
    2000000,
    3000000,
    np.inf
]

labels = [
    "< ₹5L",
    "₹5L–₹10L",
    "₹10L–₹15L",
    "₹15L–₹20L",
    "₹20L–₹30L",
    "₹30L+"
]

results["salary_band"] = pd.cut(
    results["actual_salary"],
    bins=bins,
    labels=labels,
    right=False
)


# ============================================================
# 13. BAND-LEVEL PERFORMANCE
# ============================================================

band_results = (
    results
    .groupby(
        "salary_band",
        observed=False
    )
    .agg(
        jobs=("actual_salary", "count"),

        actual_avg=("actual_salary", "mean"),

        predicted_avg=("predicted_salary", "mean"),

        mae=("absolute_error", "mean"),

        rmse=(
            "absolute_error",
            lambda x: np.sqrt(
                np.mean(x ** 2)
            )
        )
    )
    .reset_index()
)


# ============================================================
# 14. FORMAT RESULTS
# ============================================================

print("\nSalary Band Performance")
print("=" * 80)

for _, row in band_results.iterrows():

    print(
        f"{row['salary_band']:<12}"
        f" Jobs: {int(row['jobs']):>3}"
        f" | Actual Avg: ₹{row['actual_avg']:>10,.0f}"
        f" | Predicted Avg: ₹{row['predicted_avg']:>10,.0f}"
        f" | MAE: ₹{row['mae']:>10,.0f}"
        f" | RMSE: ₹{row['rmse']:>10,.0f}"
    )


# ============================================================
# 15. PREDICTION BIAS
# ============================================================

results["prediction_error"] = (
    results["predicted_salary"]
    - results["actual_salary"]
)

bias_results = (
    results
    .groupby(
        "salary_band",
        observed=False
    )["prediction_error"]
    .mean()
    .reset_index()
)

print("\nAverage Prediction Error by Salary Band")
print("=" * 60)

for _, row in bias_results.iterrows():

    print(
        f"{row['salary_band']:<12}"
        f" ₹{row['prediction_error']:>12,.0f}"
    )


# ============================================================
# 16. SAVE RESULTS
# ============================================================

OUTPUT_FILE = (
    "data/processed/"
    "salary_band_model_evaluation.csv"
)

band_results.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved band evaluation to: {OUTPUT_FILE}"
)