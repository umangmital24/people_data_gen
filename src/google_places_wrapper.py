import requests
import os
import time
import json
from urllib.parse import quote_plus
from . import config


def scrape_google_places(search_term):
    """
    Scrapes Google Places using the Text Search API, handles pagination,
    and fetches detailed information for each place.
    
    Args:
        search_term (str): The search query, e.g., "tech startups in San Francisco".
    
    Returns:
        list: A list of dictionaries with all available data for each company.
    """
    print(f"🌍 Scraping Google Places for: '{search_term}'...")
    encoded_term = quote_plus(search_term)
    
    all_results = []
    next_page_token = None
    
    # Loop to handle pagination, fetching up to 3 pages (60 results).
    page_num = 1
    for i in range(page_num):
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={encoded_term}&key={config.GOOGLE_PLACES_API_KEY}"
        
        if next_page_token:
            url += f"&pagetoken={next_page_token}"
            # A brief delay is required when using pagination to prevent a rate limit error.
            time.sleep(2)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract basic info and place_id from results
            results = data.get("results", [])
            for r in results:
                all_results.append({
                    "name": r.get("name"),
                    "address": r.get("formatted_address"),
                    "place_id": r.get("place_id")
                })
            
            # Check for a next page token for pagination
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error from Google Places: {e}")
            return []
            
    if not all_results:
        print("\nNo companies found from initial search.")
        return []

    print(f"\nFound {len(all_results)} companies. Fetching details...")
    
    complete_data = []
    
    for company in all_results:
        place_id = company.get("place_id")
        if place_id:
            print(f"🔍 Fetching details for place ID: {place_id}...")
            url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,website,formatted_phone_number,rating&key={config.GOOGLE_PLACES_API_KEY}"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                result = data.get("result")
                if result:
                    full_record = {
                        "name": result.get("name"),
                        "address": company.get("address"),
                        "place_id": place_id,
                        "website": result.get("website"),
                        "phone": result.get("formatted_phone_number"),
                        "rating": result.get("rating")
                    }
                    complete_data.append(full_record)
            
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error fetching details: {e}")
                
    return complete_data
