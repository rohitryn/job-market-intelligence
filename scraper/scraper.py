# import os
# import requests
# from dotenv import load_dotenv

# # Load credentials from .env
# load_dotenv()

# APP_ID = os.getenv("ADZUNA_APP_ID")
# APP_KEY = os.getenv("ADZUNA_APP_KEY")

# # Adzuna API endpoint
# url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# # Parameters for the API request
# params = {
#     "app_id": APP_ID,
#     "app_key": APP_KEY,
#     "results_per_page": 10,
#     "what": "data analyst",
#     "where": "India"
# }

# # Send request to Adzuna
# response = requests.get(url, params=params)

# # Check response
# print("Status Code:", response.status_code)

# if response.status_code == 200:

#     data = response.json()

#     print("Total Jobs Found:", data.get("count"))
#     print("Jobs Retrieved:", len(data.get("results", [])))

#     # Display basic information
#     for job in data.get("results", []):

#         print("\nJob ID:", job.get("id"))
#         print("Title:", job.get("title"))
#         print("Company:", job.get("company", {}).get("display_name"))
#         print("Location:", job.get("location", {}).get("display_name"))
#         print("Category:", job.get("category", {}).get("label"))
#         print("Salary Min:", job.get("salary_min"))
#         print("Salary Max:", job.get("salary_max"))
#         print("Created:", job.get("created"))
#         print("URL:", job.get("redirect_url"))

# else:
#     print("API request failed.")
#     print("Response:", response.text)

# import os
# import json
# import requests
# from dotenv import load_dotenv
# from datetime import datetime

# # Load credentials
# load_dotenv()

# APP_ID = os.getenv("ADZUNA_APP_ID")
# APP_KEY = os.getenv("ADZUNA_APP_KEY")

# # Adzuna API endpoint
# url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# params = {
#     "app_id": APP_ID,
#     "app_key": APP_KEY,
#     "results_per_page": 10,
#     "what": "data analyst",
#     "where": "India"
# }

# # Send API request
# response = requests.get(url, params=params)

# print("Status Code:", response.status_code)

# if response.status_code == 200:

#     data = response.json()

#     print("Total Jobs Found:", data.get("count"))
#     print("Jobs Retrieved:", len(data.get("results", [])))

#     # Create timestamp
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     # File path
#     file_path = f"data/raw/jobs_{timestamp}.json"

#     # Save raw API response
#     with open(file_path, "w", encoding="utf-8") as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)

#     print("Raw data saved to:", file_path)

# else:
#     print("API request failed.")
#     print("Response:", response.text)

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load credentials
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# API settings
base_url = "https://api.adzuna.com/v1/api/jobs/in/search"

results_per_page = 50
number_of_pages = 5

all_jobs = []

# Fetch multiple pages
for page in range(1, number_of_pages + 1):

    print(f"\nFetching page {page}...")

    url = f"{base_url}/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": "data analyst",
        "where": "India"
    }

    response = requests.get(url, params=params)

    print("Status Code:", response.status_code)

    if response.status_code == 200:

        data = response.json()

        jobs = data.get("results", [])

        print("Jobs Retrieved:", len(jobs))

        all_jobs.extend(jobs)

    else:
        print("API request failed.")
        print("Response:", response.text)

# Create timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save raw data
file_path = f"data/raw/jobs_{timestamp}.json"

with open(file_path, "w", encoding="utf-8") as file:

    json.dump(
        all_jobs,
        file,
        indent=4,
        ensure_ascii=False
    )

print("\n--------------------------------")
print("SCRAPING COMPLETED")
print("--------------------------------")
print("Total jobs collected:", len(all_jobs))
print("Raw data saved to:", file_path)