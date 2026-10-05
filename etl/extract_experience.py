import re
import pandas as pd


INPUT_FILE = "data/processed/master_jobs_cleaned.csv"
OUTPUT_FILE = "data/processed/master_jobs_with_experience.csv"


def clean_text(text):
    """
    Normalize description text before applying regex patterns.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    # Convert HTML entities / basic HTML
    text = re.sub(r"&nbsp;", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"&amp;", "&", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_experience(text):
    """
    Extract minimum and maximum years of experience.

    Returns:
        experience_min
        experience_max
    """

    text = clean_text(text)

    if not text:
        return None, None

    # ---------------------------------------------------------
    # 2. Explicit experience ranges
    #
    # Examples:
    # 3-8 years
    # 3 to 8 years
    # 0.00-1.00 Years
    # 2-5 years of experience
    # ---------------------------------------------------------

    range_patterns = [
        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d+(?:\.\d+)?)\s+years?\s+(?:of\s+)?(?:relevant\s+)?experience\b",

        r"\bexperience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d+(?:\.\d+)?)\s+years?\b",

        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d+(?:\.\d+)?)\s+years?\b",
    ]

    for pattern in range_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            minimum = float(match.group(1))
            maximum = float(match.group(2))

            return minimum, maximum

    # ---------------------------------------------------------
    # 3. Minimum experience
    #
    # Examples:
    # minimum 6 years' experience
    # minimum 8 years of experience
    # at least 5 years experience
    # ---------------------------------------------------------

    minimum_patterns = [
        r"\bminimum\s+of\s+(\d+(?:\.\d+)?)\s+years?\b",

        r"\bminimum\s+(\d+(?:\.\d+)?)\s+years?\b",

        r"\bat\s+least\s+(\d+(?:\.\d+)?)\s+years?\b",

        r"\b(\d+(?:\.\d+)?)\s*\+\s*years?\s+(?:of\s+)?(?:relevant\s+)?experience\b",
    ]

    for pattern in minimum_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            minimum = float(match.group(1))

            return minimum, None

    # ---------------------------------------------------------
    # 4. Simple experience statement
    #
    # Examples:
    # 7 years of experience
    # 5 years experience
    # 3 years of relevant experience
    # ---------------------------------------------------------

    simple_patterns = [
        r"\b(\d+(?:\.\d+)?)\s+years?\s+of\s+(?:relevant\s+)?experience\b",

        r"\b(\d+(?:\.\d+)?)\s+years?\s+(?:relevant\s+)?experience\b",
    ]

    for pattern in simple_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            minimum = float(match.group(1))

            return minimum, minimum

    # ---------------------------------------------------------
    # 1. Explicit fresher / entry-level indicators
    # ---------------------------------------------------------

    fresher_patterns = [
        r"\bfreshers?\b",
        r"\bfresher\s+welcome\b",
        r"\bentry[- ]level\b",
        r"\bno\s+experience\s+required\b",
        r"\b0\s+years?\s+(?:of\s+)?experience\b",
    ]

    for pattern in fresher_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return 0.0, 0.0


    return None, None


def main():

    print("Loading dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Total jobs: {len(df)}")

    # extraction...

    results = df["description"].apply(
        extract_experience

    )

    df["experience_min"] = results.apply(
        lambda x: x[0]

    )

    df["experience_max"] = results.apply(
        lambda x: x[1]

    )

    # save...

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # summary...

    jobs_with_experience = df["experience_min"].notna().sum()

    jobs_without_experience = df["experience_min"].isna().sum()

    print()
    print("========== EXPERIENCE EXTRACTION ==========")

    print(
        f"Jobs processed: {len(df)}"
    )

    print(
        f"Jobs with experience: {jobs_with_experience}"
    )


    print(
        f"Jobs without experience: {jobs_without_experience}"     
    )

    print()
    print("========== EXAMPLES ==========")

    examples = df[
        df["experience_min"].notna()
    ][
        [
            "job_id",
            "job_title",
            "experience_min",
            "experience_max",
            "description"
        ]
    ].head(20)

    # validation
    print()
    print("========== EXPERIENCE VALIDATION ==========")

    validation = df[
        df["experience_min"].notna()
    ][
        [
            "job_id",
            "job_title",
            "experience_min",
            "experience_max",
            "description"
        ]
    ].head(20)

    for _, row in validation.iterrows():

        print("\n-----------------------------------")

        print(f"Job ID: {row['job_id']}")
        print(f"Title: {row['job_title']}")

        print(
            f"Extracted: "
            f"{row['experience_min']} - "
            f"{row['experience_max']}"
        )

        print(
            f"Description: "
            f"{row['description'][:500]}"
        )


if __name__ == "__main__":
    main()