import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


BASE_URL = "https://job-boards.greenhouse.io/precisionmedicinegroup"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_job_links():
    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        timeout=20
    )

    print("Job board status:", response.status_code)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    job_links = []

    for link in soup.find_all("a", href=True):

        href = link["href"]
        title = link.get_text(" ", strip=True)

        if "/jobs/" in href:

            job_links.append({
                "title": title,
                "url": href
            })

    return job_links


def scrape_job(url):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1")

    description = soup.find(
        class_="job__description"
    )

    location = soup.find(
        class_="job__location"
    )

    job = {
        "job_title": title.get_text(" ", strip=True)
        if title else None,

        "location": location.get_text(" ", strip=True)
        if location else None,

        "description": description.get_text(
            " ",
            strip=True
        ) if description else None,

        "job_url": url,

        "source": "Greenhouse",

        "scraped_at": datetime.now().isoformat()
    }

    return job


def main():

    print("\nFinding job postings...")

    job_links = get_job_links()

    print("Job links found:", len(job_links))

    jobs = []

    for i, job_link in enumerate(job_links[:20], start=1):

        print(
            f"Scraping job {i}/{min(20, len(job_links))}: "
            f"{job_link['title']}"
        )

        try:

            job = scrape_job(job_link["url"])

            jobs.append(job)

        except Exception as e:

            print("Failed:", e)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_file = (
        f"data/raw/greenhouse_jobs_{timestamp}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            jobs,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n-----------------------------")
    print("WEB SCRAPING COMPLETED")
    print("-----------------------------")
    print("Jobs scraped:", len(jobs))
    print("Saved to:", output_file)


if __name__ == "__main__":
    main()