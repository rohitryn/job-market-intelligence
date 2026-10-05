import requests
import json
import time
from datetime import datetime


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BOARD_TOKENS = [
    "precisionmedicinegroup",
    "capco",
    "sigmoid",
    "launchdarkly",
    "earnin",
    "gomotive",
    "doordashindia",
    "episodesix",
    "aidashinc",
    "neweratech",
    "celonis",
    "coherehealth",
    "karya",
]

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

HEADERS = {
    "User-Agent": "JobMarketIntelligencePortfolio/1.0"
}


# --------------------------------------------------
# GET JOBS FROM ONE COMPANY
# --------------------------------------------------

def get_company_jobs(board_token):

    url = f"{BASE_URL}/{board_token}/jobs"

    params = {
        "content": "true"
    }

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    print(
        f"{board_token}: "
        f"HTTP {response.status_code}"
    )

    response.raise_for_status()

    data = response.json()

    return data.get("jobs", [])


# --------------------------------------------------
# STANDARDIZE JOB
# --------------------------------------------------

def standardize_job(job, board_token):

    location = job.get("location") or {}

    return {
        "source": "Greenhouse",

        "source_company": board_token,

        "source_job_id": job.get("id"),

        "job_title": job.get("title"),

        "location": location.get("name"),

        "absolute_url": job.get("absolute_url"),

        "updated_at": job.get("updated_at"),

        "content": job.get("content"),

        "departments": job.get("departments"),

        "offices": job.get("offices")
    }


# --------------------------------------------------
# MAIN COLLECTOR
# --------------------------------------------------

def main():

    all_jobs = []

    print("\n===================================")
    print("GREENHOUSE JOB COLLECTOR")
    print("===================================\n")

    for board_token in BOARD_TOKENS:

        print(
            f"Collecting jobs from: "
            f"{board_token}"
        )

        try:

            jobs = get_company_jobs(board_token)

            print(
                f"Jobs found: {len(jobs)}"
            )

            for job in jobs:

                standardized = standardize_job(
                    job,
                    board_token
                )

                all_jobs.append(standardized)

            # Be polite to the API
            time.sleep(1)

        except Exception as e:

            print(
                f"Failed for {board_token}: {e}"
            )

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    unique_jobs = {}

    for job in all_jobs:

        key = (
            job["source_company"],
            job["source_job_id"]
        )

        unique_jobs[key] = job

    all_jobs = list(unique_jobs.values())

    print("\n===================================")
    print("COLLECTION COMPLETED")
    print("===================================")

    print(
        "Total unique jobs:",
        len(all_jobs)
    )

    # --------------------------------------------------
    # SAVE RAW DATA
    # --------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = (
        f"data/raw/"
        f"greenhouse_raw_{timestamp}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_jobs,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Raw data saved to:",
        output_file
    )


if __name__ == "__main__":
    main()