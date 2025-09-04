import time
import requests
import neverbounce_sdk
from . import config

def find_contacts_with_apollo(domain: str):
    """
    Finds contacts for a domain using Apollo.io's REST API.
    This uses the '/mixed_people/search' endpoint to discover new contacts
    based on a domain and predefined job titles (personas).
    """
    print(f"🔎 Searching Apollo for contacts at '{domain}'...")
    
    url = "https://api.apollo.io/v1/mixed_people/search"

    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json"
    }

    payload = {
        "api_key": config.APOLLO_API_KEY,
        "q_organization_domains": domain,
        "person_titles": config.CONTACT_PERSONAS,
        "per_page": 5 # Limit the number of contacts to find per company
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        
        people = response.json().get('people', [])
        contacts = [
            {"name": p.get('name'), "title": p.get('title'), "email": p.get('email')}
            for p in people if p.get('email')
        ]
        print(f"✅ Found {len(contacts)} contacts at {domain}.")
        return contacts
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Apollo API error for {domain}: {e}")
        return []

def validate_emails_with_neverbounce(emails: list):
    """
    Validates a list of emails using the official neverbounce-sdk.
    Follows the bulk job workflow: create -> start -> status -> results.
    """
    if not emails:
        return {}
        
    print(f"✅ Validating {len(emails)} emails with NeverBounce...")
    
    try:
        client = neverbounce_sdk.client(api_key=config.NEVERBOUNCE_API_KEY, timeout=30)
        emails_to_submit = [{'email': email} for email in emails]
        
        job_info = client.jobs_create(emails_to_submit)
        job_id = job_info['id']
        
        client.jobs_parse(job_id=job_id, auto_start=True)
        
        while True:
            status = client.jobs_status(job_id)
            if status['job_status'] == 'complete':
                print(f"   NeverBounce job {job_id} is complete.")
                break
            print(f"   NeverBounce job {job_id} is {status['job_status']} ({status['percent_complete']}%)... waiting 5s.")
            time.sleep(5)
            
        validation_map = {}
        results_iterator = client.jobs_results(job_id)
        
        for item in results_iterator:
            email = item.get('email')
            result = item.get('verification', {}).get('result')
            if email and result:
                validation_map[email] = result
            
        return validation_map

    except Exception as e:
        print(f"⚠️ NeverBounce SDK error: {e}")
        return {}