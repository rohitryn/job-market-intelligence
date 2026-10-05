import os
import json
import time
import requests

from dotenv import load_dotenv
from datetime import datetime


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search"


# --------------------------------------------------
# JOB SEARCH QUERIES
# --------------------------------------------------

SEARCH_QUERIES = [
    "data analyst",
    "business analyst",
    "bi analyst",
    "business intelligence analyst",
    "reporting analyst",
    "data scientist",
    "data engineer",
    "analytics engineer",
    "product analyst",
    "financial analyst",
    "marketing analyst",
]


# --------------------------------------------------
# LOCATIONS
# --------------------------------------------------

LOCATIONS = [
    "India",
    "Bangalore",
    "Hyderabad",
    "Mumbai",
    "Pune",
    "Chennai",
    "Delhi",
    "Gurgaon",
    "Noida",
    "Kolkata",
]


# --------------------------------------------------
# API SETTINGS
# --------------------------------------------------

RESULTS_PER_PAGE = 50

# Start conservatively.
# We can increase this after checking the API results.
PAGES_PER_QUERY = 2

HEADERS = {
    "User-Agent": "JobMarketIntelligencePortfolio/1.0"
}


# ==================================================
# FETCH ONE PAGE
# ==================================================

def fetch_jobs(query, location, page):

    url = f"{BASE_URL}/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": query,
        "where": location,
        "content-type": "application/json"
    }

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    print(
        f"{query:<25} | "
        f"{location:<15} | "
        f"page {page:<2} | "
        f"HTTP {response.status_code}"
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# MAIN COLLECTOR
# ==================================================

def main():

    print("\n==========================================")
    print("ADZUNA LARGE-SCALE JOB COLLECTOR")
    print("==========================================\n")

    all_jobs = []

    total_requests = 0

    for query in SEARCH_QUERIES:

        for location in LOCATIONS:

            print(
                f"\nSearching: '{query}' "
                f"in '{location}'"
            )

            for page in range(
                1,
                PAGES_PER_QUERY + 1
            ):

                try:

                    data = fetch_jobs(
                        query,
                        location,
                        page
                    )

                    jobs = data.get(
                        "results",
                        []
                    )

                    print(
                        f"  Jobs returned: {len(jobs)}"
                    )

                    # Add metadata so we know
                    # how the job was collected.
                    for job in jobs:

                        job["_collection_query"] = query
                        job["_collection_location"] = location

                    all_jobs.extend(jobs)

                    total_requests += 1

                    # Stay comfortably below
                    # the API rate limit.
                    time.sleep(2)

                except Exception as e:

                    print(
                        f"  ERROR: {e}"
                    )

                    # Continue with next request
                    continue


    # ==================================================
    # DEDUPLICATION
    # ==================================================

    print("\n==========================================")
    print("DEDUPLICATING")
    print("==========================================")

    unique_jobs = {}

    for job in all_jobs:

        job_id = job.get("id")

        if job_id is not None:

            unique_jobs[job_id] = job


    unique_jobs = list(
        unique_jobs.values()
    )


    # ==================================================
    # SAVE DATA
    # ==================================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = (
        f"data/raw/"
        f"adzuna_large_{timestamp}.json"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            unique_jobs,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ==================================================
    # SUMMARY
    # ==================================================

    print("\n==========================================")
    print("COLLECTION COMPLETED")
    print("==========================================")

    print(
        "API requests made:",
        total_requests
    )

    print(
        "Raw records collected:",
        len(all_jobs)
    )

    print(
        "Unique jobs:",
        len(unique_jobs)
    )

    print(
        "Duplicate records removed:",
        len(all_jobs) - len(unique_jobs)
    )

    print(
        "Raw file:",
        output_file
    )


if __name__ == "__main__":
    main()