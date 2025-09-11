import json
import os
from src import google_places_wrapper
from src import gen_search_terms, data_processor, contact_finder, email_verifier
from src.config import PRODUCT_DESCRIPTION, lead_plan_file, linkedin_data_file, google_places_data_file, merged_data_file, verified_employees_file, industry_filter, country_filter

def save_data(data, filename):
    """Saves data to a JSON file."""
    if data:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"\n✅ Successfully saved {len(data)} records to '{filename}'.")
    else:
        print(f"\nNo data to save to '{filename}'.")

if __name__ == "__main__":
    print("--- Starting Lead Generation Pipeline ---")

    # This dictionary makes the pipeline flexible.
    # Set any step to False to skip it.
    pipeline_config = {
        "generate_search_terms": True,
        "scrape_google_places": True,
        "process_and_merge_data": False,
        "find_and_verify_contacts": False,
    }

    # --- Step 1: Generate Search Terms from Product Description ---
    search_terms = []
    if pipeline_config["generate_search_terms"]:
        print("\n--- Step 1: Generating Google Places search terms ---")
        lead_plan = gen_search_terms.generate_lead_generation_plan(PRODUCT_DESCRIPTION)
        # Save the lead_plan to a JSON file
        save_data(lead_plan, lead_plan_file)
        if not lead_plan:
            print("❌ Failed to generate a lead plan. Exiting.")
            exit()
        for group in lead_plan:
            search_terms.extend(group.get("google_search_terms", []))
    
    # --- Step 2: Scrape Google Places using the generated terms ---
    if pipeline_config["scrape_google_places"]:
        if not search_terms:
            print("❌ No search terms available. Skipping Google Places scraping.")
        else:
            print("\n--- Step 2: Scraping Google Places for company data ---")
            google_places_data = []
            for term in search_terms:
                companies = google_places_wrapper.scrape_google_places(term)
                google_places_data.extend(companies)
            
            save_data(google_places_data, google_places_data_file)

    # --- Step 3: Process, Filter, and Merge Data ---
    if pipeline_config["process_and_merge_data"]:
        print("\n--- Step 3: Filtering, merging, and deduplicating data ---")
        
        data_processor.run_data_pipeline(
            linkedin_data_file,
            google_places_data_file,
            industry_filter,
            country_filter,
            merged_data_file
        )

    # --- Step 4: Find and Verify Contacts ---
    if pipeline_config["find_and_verify_contacts"]:
        print("\n--- Step 4: Finding and verifying contacts ---")
        
        contact_finder.find_and_verify_contacts(
            input_file=merged_data_file,
            output_file=verified_employees_file
        )
    
    print("\n--- Pipeline finished successfully! ---")
