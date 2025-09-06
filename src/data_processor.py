import json

def load_json_data(filepath):
    """Loads data from a JSON file."""
    try:
        # Added encoding='utf-8' to handle Unicode characters
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        return None

def filter_linkedin_data(companies, industry_filter, country_filter):
    """
    Filters a list of LinkedIn company data based on industry and country.
    
    Args:
        companies (list): A list of dictionaries, where each dictionary is a company's data.
        industry_filter (str): The industry to filter by.
        country_filter (str): The two-letter country code to filter by.
        
    Returns:
        list: A new list containing only the companies that match the filters.
    """
    filtered_companies = []
    
    for company in companies:
        if "industries" in company and "country_codes_array" in company:
            # The 'industries' field is a string, check if the filter is a substring
            industries_match = industry_filter in company["industries"]
            # The 'country_codes_array' field is a list, check if the filter is in the list
            country_match = country_filter in company["country_codes_array"]

            if industries_match and country_match:
                filtered_companies.append(company)

    return filtered_companies

def merge_and_deduplicate(linkedin_data, places_data):
    """
    Merges two lists of company data and removes duplicates.
    Prioritizes LinkedIn data if a company exists in both lists.
    
    Args:
        linkedin_data (list): A list of filtered company data from LinkedIn.
        places_data (list): A list of company data from Google Places.
        
    Returns:
        list: The merged and deduplicated list of company data.
    """
    # Create a dictionary for efficient lookup, using website as the key
    merged_companies = {
        company.get("website"): company
        for company in linkedin_data if company.get("website")
    }

    # Iterate through the places data and merge or add
    for place_company in places_data:
        website = place_company.get("website")
        if website and website in merged_companies:
            # Company exists in both lists, keep the more comprehensive LinkedIn data
            # but update with any missing fields from Google Places data if needed
            linkedin_company = merged_companies[website]
            for key, value in place_company.items():
                if key not in linkedin_company:
                    linkedin_company[key] = value
        elif website:
            # Company is unique to the Places data, so add it
            merged_companies[website] = place_company
        else:
            # If no website is available, append the company from Places API to the final list,
            # as we can't reliably deduplicate it.
            merged_companies[place_company.get("name")] = place_company

    return list(merged_companies.values())

def run_data_pipeline(linkedin_filepath, places_filepath, industry_to_find, country_to_find, output_filename):
    """
    Runs the entire data processing pipeline: loads, filters, merges, and saves data.
    """
    # --- Step 1: Filter LinkedIn Data ---
    print("--- Step 1: Filtering LinkedIn data ---")
    linkedin_raw_data = load_json_data(linkedin_filepath)
    
    if linkedin_raw_data:
        filtered_linkedin_data = filter_linkedin_data(linkedin_raw_data, industry_to_find, country_to_find)
        print(f"Found {len(filtered_linkedin_data)} companies in LinkedIn data that match the criteria.")
    else:
        filtered_linkedin_data = []

    # --- Step 2: Load Google Places Data ---
    print("\n--- Step 2: Loading Google Places data ---")
    places_data = load_json_data(places_filepath)
    if places_data:
        print(f"Loaded {len(places_data)} companies from Google Places data.")
    else:
        places_data = []
    
    # --- Step 3: Merge and deduplicate the data ---
    print("\n--- Step 3: Merging and deduplicating data ---")
    final_merged_data = merge_and_deduplicate(filtered_linkedin_data, places_data)
    
    # --- Step 4: Save the final result ---
    if final_merged_data:
        with open(output_filename, "w") as f:
            json.dump(final_merged_data, f, indent=4)
        print(f"\n✅ Successfully saved {len(final_merged_data)} unique companies to '{output_filename}'.")
    else:
        print("\nNo data to save after merging.")

if __name__ == "__main__":
    # Define file paths and filtering criteria
    linkedin_filepath = "LinkedIn_company_information.json"
    places_filepath = "companies.json"
    output_filename = "final_merged_companies.json"
    
    industry_to_find = "Information Technology & Services"
    country_to_find = "IN"

    # Run the entire data processing pipeline with a single function call
    run_data_pipeline(linkedin_filepath, places_filepath, industry_to_find, country_to_find, output_filename)


