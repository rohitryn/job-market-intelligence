import pandas as pd

FILE = "data/processed/ml_salary_dataset.csv"

df = pd.read_csv(FILE)

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nFirst 5 rows:")
print(df.head())