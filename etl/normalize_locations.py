import os
import re
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

OUTPUT_FILE = "data/processed/normalized_locations.csv"


# ==================================================
# CITY ALIASES
# ==================================================

CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",

    "hyderabad": "Hyderabad",
    "hyderbad": "Hyderabad",

    "pune": "Pune",

    "mumbai": "Mumbai",
    "bombay": "Mumbai",

    "chennai": "Chennai",
    "madras": "Chennai",

    "delhi": "Delhi",

    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",

    "noida": "Noida",

    "kolkata": "Kolkata",
    "calcutta": "Kolkata",

    "ahmedabad": "Ahmedabad",
    "chandigarh": "Chandigarh",
    "coimbatore": "Coimbatore",
    "gandhinagar": "Gandhinagar",
    "indore": "Indore",
    "kochi": "Kochi",
    "mangalore": "Mangalore",
    "trivandrum": "Trivandrum",
    "vadodara": "Vadodara",
    "raipur": "Raipur",
    "panipat": "Panipat",
    "palwal": "Palwal",

    "amsterdam": "Amsterdam",
    "atlanta": "Atlanta",
    "austin": "Austin",
    "berlin": "Berlin",
    "bratislava": "Bratislava",
    "brisbane": "Brisbane",
    "buenos aires": "Buenos Aires",
    "chicago": "Chicago",
    "copenhagen": "Copenhagen",
    "dallas": "Dallas",
    "doha": "Doha",
    "dusseldorf": "Dusseldorf",
    "edinburgh": "Edinburgh",
    "frankfurt": "Frankfurt",
    "fort wayne": "Fort Wayne",
    "frederick": "Frederick",
    "glasgow": "Glasgow",
    "hong kong": "Hong Kong",
    "islamabad": "Islamabad",
    "kuala lumpur": "Kuala Lumpur",
    "lahore": "Lahore",
    "london": "London",
    "madrid": "Madrid",
    "melbourne": "Melbourne",
    "mexico city": "Mexico City",
    "milan": "Milan",
    "montreal": "Montreal",
    "monterrey": "Monterrey",
    "munich": "Munich",
    "nashville": "Nashville",
    "new york": "New York",
    "new york city": "New York",
    "oamaru": "Oamaru",
    "oakland": "Oakland",
    "orlando": "Orlando",
    "palo alto": "Palo Alto",
    "paris": "Paris",
    "perth": "Perth",
    "philadelphia": "Philadelphia",
    "quincy": "Quincy",
    "raleigh": "Raleigh",
    "redwood city": "Redwood City",
    "riyadh": "Riyadh",
    "san francisco": "San Francisco",
    "san jose": "San Jose",
    "salt lake city": "Salt Lake City",
    "seattle": "Seattle",
    "seoul": "Seoul",
    "singapore": "Singapore",
    "slough": "Slough",
    "stockholm": "Stockholm",
    "sydney": "Sydney",
    "taipei": "Taipei",
    "tokyo": "Tokyo",
    "toronto": "Toronto",
    "vancouver": "Vancouver",
    "washington": "Washington",
    "winston-salem": "Winston-Salem",
    "zurich": "Zurich",
    "zürich": "Zurich",
}


# ==================================================
# COUNTRY ALIASES
# ==================================================

COUNTRY_ALIASES = {
    "india": "India",
    "united states": "United States",
    "us": "United States",
    "usa": "United States",
    "canada": "Canada",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "australia": "Australia",
    "germany": "Germany",
    "france": "France",
    "italy": "Italy",
    "spain": "Spain",
    "netherlands": "Netherlands",
    "belgium": "Belgium",
    "brazil": "Brazil",
    "argentina": "Argentina",
    "mexico": "Mexico",
    "poland": "Poland",
    "ireland": "Ireland",
    "japan": "Japan",
    "china": "China",
    "hong kong": "Hong Kong",
    "malaysia": "Malaysia",
    "new zealand": "New Zealand",
    "pakistan": "Pakistan",
    "philippines": "Philippines",
    "singapore": "Singapore",
    "south korea": "South Korea",
    "taiwan": "Taiwan",
    "thailand": "Thailand",
    "turkey": "Turkey",
    "switzerland": "Switzerland",
    "slovakia": "Slovakia",
    "czech republic": "Czech Republic",
    "dominican republic": "Dominican Republic",
    "hungary": "Hungary",
    "romania": "Romania",
    "serbia": "Serbia",
    "slovenia": "Slovenia",
    "united arab emirates": "United Arab Emirates",
    "chile": "Chile",
}


# ==================================================
# TEXT CLEANING
# ==================================================

def clean_text(value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    value = re.sub(r"\s+", " ", value)

    return value


# ==================================================
# LOCATION TYPE
# ==================================================

def detect_location_type(location):
    text = location.lower()

    if ";" in text:
        return "Multi-location"

    if "remote" in text:
        return "Remote"

    if "hybrid" in text:
        return "Hybrid"

    if text == "middle east":
        return "Region"

    return "Location"


def find_city(location):
    text = location.lower()

    # Multi-location records should not be assigned
    # to one arbitrary city.
    if ";" in text:
        return None

    # Specific city patterns first.
    # This prevents "Buffalo, New York" from becoming New York.
    city_patterns = [
        (r"\bbuffalo\b", "Buffalo"),
        (r"\baustin\b", "Austin"),
        (r"\bnashville\b", "Nashville"),
        (r"\bsan francisco\b", "San Francisco"),
        (r"\bsan jose\b", "San Jose"),
        (r"\bredwood city\b", "Redwood City"),
        (r"\bfort wayne\b", "Fort Wayne"),
        (r"\bnew york city\b", "New York"),
        (r"\bnew york\b", "New York"),
        (r"\bwashington dc\b", "Washington"),
        (r"\bwashington\b", "Washington"),
        (r"\bmountain view\b", "Mountain View"),
        (r"\bpalo alto\b", "Palo Alto"),
        (r"\bsalt lake city\b", "Salt Lake City"),
        (r"\bwinston-salem\b", "Winston-Salem"),

        (r"\bbangalore\b", "Bengaluru"),
        (r"\bbengaluru\b", "Bengaluru"),
        (r"\bhyderabad\b", "Hyderabad"),
        (r"\bhyderbad\b", "Hyderabad"),
        (r"\bpune\b", "Pune"),
        (r"\bmumbai\b", "Mumbai"),
        (r"\bbombay\b", "Mumbai"),
        (r"\bchennai\b", "Chennai"),
        (r"\bmadras\b", "Chennai"),
        (r"\bdelhi\b", "Delhi"),
        (r"\bgurgaon\b", "Gurugram"),
        (r"\bgurugram\b", "Gurugram"),
        (r"\bnoida\b", "Noida"),
        (r"\bkolkata\b", "Kolkata"),
        (r"\bcalcutta\b", "Kolkata"),

        (r"\bahmedabad\b", "Ahmedabad"),
        (r"\bchandigarh\b", "Chandigarh"),
        (r"\bcoimbatore\b", "Coimbatore"),
        (r"\bgandhinagar\b", "Gandhinagar"),
        (r"\bindore\b", "Indore"),
        (r"\bkochi\b", "Kochi"),
        (r"\bmangalore\b", "Mangalore"),
        (r"\btrivandrum\b", "Trivandrum"),
        (r"\bvadodara\b", "Vadodara"),
        (r"\braipur\b", "Raipur"),
        (r"\bpanipat\b", "Panipat"),
        (r"\bpalwal\b", "Palwal"),

        (r"\bamsterdam\b", "Amsterdam"),
        (r"\batlanta\b", "Atlanta"),
        (r"\bberlin\b", "Berlin"),
        (r"\bbratislava\b", "Bratislava"),
        (r"\bbrisbane\b", "Brisbane"),
        (r"\bbuenos aires\b", "Buenos Aires"),
        (r"\bchicago\b", "Chicago"),
        (r"\bcopenhagen\b", "Copenhagen"),
        (r"\bdallas\b", "Dallas"),
        (r"\bdoha\b", "Doha"),
        (r"\bdusseldorf\b", "Dusseldorf"),
        (r"\bedinburgh\b", "Edinburgh"),
        (r"\bfrankfurt\b", "Frankfurt"),
        (r"\bfrederick\b", "Frederick"),
        (r"\bglasgow\b", "Glasgow"),
        (r"\bhong kong\b", "Hong Kong"),
        (r"\bislamabad\b", "Islamabad"),
        (r"\bkuala lumpur\b", "Kuala Lumpur"),
        (r"\blahore\b", "Lahore"),
        (r"\blondon\b", "London"),
        (r"\bmadrid\b", "Madrid"),
        (r"\bmelbourne\b", "Melbourne"),
        (r"\bmexico city\b", "Mexico City"),
        (r"\bmilan\b", "Milan"),
        (r"\bmontreal\b", "Montreal"),
        (r"\bmonterrey\b", "Monterrey"),
        (r"\bmunich\b", "Munich"),
        (r"\boakland\b", "Oakland"),
        (r"\borlando\b", "Orlando"),
        (r"\bparis\b", "Paris"),
        (r"\bperth\b", "Perth"),
        (r"\bquincy\b", "Quincy"),
        (r"\braleigh\b", "Raleigh"),
        (r"\briyadh\b", "Riyadh"),
        (r"\bseattle\b", "Seattle"),
        (r"\bseoul\b", "Seoul"),
        (r"\bsingapore\b", "Singapore"),
        (r"\bslough\b", "Slough"),
        (r"\bstockholm\b", "Stockholm"),
        (r"\bsydney\b", "Sydney"),
        (r"\btaipei\b", "Taipei"),
        (r"\btokyo\b", "Tokyo"),
        (r"\btoronto\b", "Toronto"),
        (r"\bvancouver\b", "Vancouver"),
        (r"\bzürich\b", "Zurich"),
        (r"\bzurich\b", "Zurich"),
        (r"\bvienna\b", "Vienna"),
        (r"\bbarasat\b", "Barasat"),
        (r"\bbarker,\s*ny\b", "Barker"),
        (r"\bcromwell,\s*ct\b", "Cromwell"),
        (r"\bindianapolis,\s*in\b", "Indianapolis"),
        (r"\bmanila\b", "Manila"),
        (r"\bnew albany,\s*oh\b", "New Albany"),
        (r"\bplano,\s*tx\b", "Plano"),
        (r"\bsouth bend,\s*in\b", "South Bend"),
        (r"\btexas\b", "Texas"),
        (r"\bwest chester,\s*pa\b", "West Chester"),       
    ]

    for pattern, canonical in city_patterns:
        if re.search(pattern, text):
            return canonical

    return None


def find_country(location):
    text = location.lower()

    # Multi-location:
    # only assign a country if every listed location
    # belongs to the same country.
    if ";" in text:
        parts = [part.strip() for part in text.split(";")]

        detected = []

        for part in parts:
            country = find_single_country(part)

            if country:
                detected.append(country)

        detected = list(set(detected))

        if len(detected) == 1:
            return detected[0]

        return None

    return find_single_country(text)


def find_single_country(text):

    country_patterns = [
        (r"\bindia\b", "India"),
        (r"\bunited states\b", "United States"),
        (r"\busa\b", "United States"),
        (r"\bus\b", "United States"),
        (r"\bcanada\b", "Canada"),
        (r"\bunited kingdom\b", "United Kingdom"),
        (r"\buk\b", "United Kingdom"),
        (r"\baustralia\b", "Australia"),
        (r"\bgermany\b", "Germany"),
        (r"\bfrance\b", "France"),
        (r"\bitaly\b", "Italy"),
        (r"\bspain\b", "Spain"),
        (r"\bnetherlands\b", "Netherlands"),
        (r"\bbelgium\b", "Belgium"),
        (r"\bbrazil\b", "Brazil"),
        (r"\bargentina\b", "Argentina"),
        (r"\bmexico\b", "Mexico"),
        (r"\bpoland\b", "Poland"),
        (r"\bireland\b", "Ireland"),
        (r"\bjapan\b", "Japan"),
        (r"\bchina\b", "China"),
        (r"\bhong kong\b", "Hong Kong"),
        (r"\bmalaysia\b", "Malaysia"),
        (r"\bnew zealand\b", "New Zealand"),
        (r"\bpakistan\b", "Pakistan"),
        (r"\bphilippines\b", "Philippines"),
        (r"\bsingapore\b", "Singapore"),
        (r"\bsouth korea\b", "South Korea"),
        (r"\btaiwan\b", "Taiwan"),
        (r"\bthailand\b", "Thailand"),
        (r"\bturkey\b", "Turkey"),
        (r"\bswitzerland\b", "Switzerland"),
        (r"\bslovakia\b", "Slovakia"),
        (r"\bczech republic\b", "Czech Republic"),
        (r"\bdominican republic\b", "Dominican Republic"),
        (r"\bhungary\b", "Hungary"),
        (r"\bromania\b", "Romania"),
        (r"\bserbia\b", "Serbia"),
        (r"\bunited arab emirates\b", "United Arab Emirates"),
        (r"\bchile\b", "Chile"),
        (r"\baustria\b", "Austria"),
        (r"\bindia\b", "India"),
        (r"\bunited states\b", "United States"),
        (r"\bphilippines\b", "Philippines"),
        (r"\bcanada\b", "Canada"),
        (r"\bprovince of quebec\b", "Canada")
    ]

    for pattern, canonical in country_patterns:
        if re.search(pattern, text):
            return canonical

    return None


# ==================================================
# MAIN NORMALIZATION
# ==================================================

def main():

    print("Loading locations from PostgreSQL...")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    query = """
        SELECT
            location_id,
            location_name
        FROM analytics.locations
        ORDER BY location_id;
    """

    df = pd.read_sql(query, conn)

    conn.close()

    print(f"Locations loaded: {len(df)}")

    # Clean
    df["location_name"] = df["location_name"].apply(clean_text)

    # Detect type
    df["location_type"] = df["location_name"].apply(
        detect_location_type
    )

    # Extract city
    df["city_normalized"] = df["location_name"].apply(
        find_city
    )

    # Extract country
    df["country_normalized"] = df["location_name"].apply(
        find_country
    )

    # Save
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("========== LOCATION NORMALIZATION ==========")

    print(f"Total locations: {len(df)}")

    print()
    print("Location types:")
    print(
        df["location_type"]
        .value_counts()
        .to_string()
    )

    print()
    print("Cities detected:")
    print(
        df["city_normalized"]
        .notna()
        .sum()
    )

    print()
    print("Countries detected:")
    print(
        df["country_normalized"]
        .notna()
        .sum()
    )

    print()
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()