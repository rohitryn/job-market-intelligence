import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Adzuna India job search endpoint
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 10,
    "what": "data analyst",
    "where": "India"
}

response = requests.get(url, params=params)

print("Status Code:", response.status_code)

if response.status_code == 200:

    data = response.json()

    print("Total Jobs Found:", data.get("count"))

    print("\nFirst 10 Jobs:\n")

    # for job in data.get("results", []):

    #     print("Title:", job.get("title"))
    #     print("Company:", job.get("company", {}).get("display_name"))
    #     print("Location:", job.get("location", {}).get("display_name"))
    #     print("Salary Min:", job.get("salary_min"))
    #     print("Salary Max:", job.get("salary_max"))
    #     print("-" * 50)
    for job in data.get("results", [])[:3]:

        print("\nJOB DATA:")
        print(job)
else:
    print("API request failed.")
    print("Response:", response.text)