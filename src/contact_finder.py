import requests
import json
from urllib.parse import urlparse
import os
from . import config
from .email_verifier import verify_email

# --- HELPER FUNCTIONS ---
def get_domain(url):
    """Extracts the domain name from a URL."""
    try:
        parsed_uri = urlparse(url)
        domain = parsed_uri.netloc
        return domain[4:] if domain.startswith('www.') else domain
    except Exception:
        return None

# --- MAIN SCRIPT FUNCTION ---
def find_and_verify_contacts(input_file, output_file):
    """
    Finds employees for companies in the input file, verifies their emails, and saves the result.
    
    Args:
        input_file (str): The path to the JSON file containing company data.
        output_file (str): The path where the verified employee data will be saved.
    """
    if not config.APOLLO_API_KEY or not config.NEVERBOUNCE_API_KEY:
        print("⚠️  Error: Please provide both your Apollo and NeverBounce API keys in src/config.py.")
        return

    all_verified_employees = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            companies_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: The file '{input_file}' was not found. Please run the previous steps.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from '{input_file}'.")
        return

    for company in companies_data:
        company_name = company.get("name", "Unknown")
        domain = get_domain(company.get("website", ""))

        if not domain:
            print(f"\n--- Skipping {company_name}: Invalid website. ---")
            continue

        print(f"\n--- Processing: {company_name} ({domain}) ---")

        # STEP 1: Find the company ID
        company_id = None
        try:
            enrich_url = "https://api.apollo.io/api/v1/organizations/enrich"
            headers = {"X-Api-Key": config.APOLLO_API_KEY, "Content-Type": "application/json"}
            params = {"domain": domain}
            response = requests.get(enrich_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            company_id = data.get("organization", {}).get("id")
            if company_id:
                print(f"✅ Found Apollo Company ID: {company_id}")
            else:
                print(f"❌ Could not find company ID for {domain}.")
                continue
        except requests.exceptions.HTTPError as err:
            print(f"❌ HTTP Error finding company: {err}")
            continue

        # STEP 2: Find all employees
        page = 1
        try:
            while True:
                search_url = "https://api.apollo.io/v1/mixed_people/search"
                payload = {"q_organization_ids": [company_id], "page": page}
                search_response = requests.post(search_url, headers=headers, json=payload)
                search_response.raise_for_status()
                search_data = search_response.json()
                people = search_data.get("people", [])

                if not people:
                    break

                # STEP 3: Verify emails and append valid ones to the list
                for person in people:
                    email = person.get("email")
                    verification_result = email_verifier.verify_email(email)
                    print(f"  - Verifying {email}... Result: {verification_result.upper()}")

                    if verification_result == 'valid':
                        person['email_verification_status'] = verification_result
                        all_verified_employees.append(person)

                page += 1
        except requests.exceptions.HTTPError as err:
            print(f"❌ HTTP Error finding employees: {err}")

    # STEP 4: Save the final list to the output file
    if all_verified_employees:
        print(f"\n✅ Writing {len(all_verified_employees)} verified employees to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_verified_employees, f, indent=4)
        print("--- Script finished successfully! ---")
    else:
        print("\n--- Script finished. No verified employees were found. ---")
