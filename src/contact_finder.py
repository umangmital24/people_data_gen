

# --- CONFIGURATION ---
# IMPORTANT: Replace "YOUR_APOLLO_API_KEY" with your actual Apollo.io API key.


# --- CONFIGURATION ---
# IMPORTANT: Replace with your new, regenerated Apollo.io API key.
API_KEY = "EpGiGtEG4FyQRyd7hXHA6A"
import requests
import json
from urllib.parse import urlparse

# --- CONFIGURATION ---
COMPANIES_FILE = "companies.json"

# --- HELPER FUNCTION ---
def get_domain(url):
    """Extracts the domain name from a URL."""
    try:
        parsed_uri = urlparse(url)
        domain = parsed_uri.netloc
        return domain[4:] if domain.startswith('www.') else domain
    except Exception:
        return None

# --- MAIN SCRIPT ---
if API_KEY == "YOUR_NEW_API_KEY_HERE":
    print("⚠️  Error: Please replace with your actual API key.")
else:
    try:
        with open(COMPANIES_FILE, 'r') as f:
            companies_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: The file '{COMPANIES_FILE}' was not found.")
        companies_data = []

    for company in companies_data:
        company_name = company.get("name", "Unknown Company")
        domain = get_domain(company.get("website", ""))

        if not domain:
            print(f"\n--- Skipping {company_name}: Invalid or missing website. ---")
            continue

        print(f"\n--- Processing: {company_name} ({domain}) ---")

        # STEP 1: Find the company ID (This part is now correct)
        company_id = None
        try:
            enrich_url = "https://api.apollo.io/api/v1/organizations/enrich"
            headers = {
                "X-Api-Key": API_KEY,
                "Content-Type": "application/json"
            }
            params = {
                "domain": domain
            }
            
            response = requests.get(enrich_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            company_id = data.get("organization", {}).get("id")

            if company_id:
                print(f"✅ Found Apollo Company ID: {company_id}")
            else:
                print(f"❌ Could not find company ID for {domain} in Apollo's response.")
                continue

        except requests.exceptions.HTTPError as err:
            print(f"❌ HTTP Error finding company: {err}")
            print(f"    Response Body: {err.response.text}")
            continue

        # STEP 2: Find people at that company using the ID
        all_employees = []
        page = 1
        try:
            while True:
                search_url = "https://api.apollo.io/v1/mixed_people/search"
                
                # --- THIS IS THE FINAL CHANGE ---
                # Create headers for the search request.
                search_headers = {
                    "X-Api-Key": API_KEY,
                    "Content-Type": "application/json"
                }
                # Remove the api_key from the payload.
                payload = {
                    "q_organization_ids": [company_id],
                    "page": page
                }
                
                search_response = requests.post(search_url, headers=search_headers, json=payload)
                search_response.raise_for_status()
                search_data = search_response.json()

                people = search_data.get("people", [])
                if not people:
                    break

                all_employees.extend(people)
                page += 1

            print(f"✅ Found {len(all_employees)} employees for {company_name}.")

        except requests.exceptions.HTTPError as err:
            print(f"❌ HTTP Error finding employees: {err}")
            print(f"    Response Body: {err.response.text}")