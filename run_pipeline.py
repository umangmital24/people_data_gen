# run_pipeline.py
import pandas as pd
from src import config, llm_handler, scraper, data_processor, contact_finder

def main():
    """Main function to orchestrate the lead generation pipeline."""
    
    # === PHASE 1: IDEATION ===
    target_groups = llm_handler.get_target_groups(config.PRODUCT_DESCRIPTION)
    
    # === PHASE 2: DATA COLLECTION ===
    all_linkedin_data = []
    all_google_data = []
    for group in target_groups:
        search_terms = llm_handler.get_search_terms(group)
        for term in search_terms.get("linkedin_terms", []):
            all_linkedin_data.extend(scraper.scrape_data_via_brightdata(term))
        for term in search_terms.get("google_terms", []):
            all_google_data.extend(scraper.scrape_google_places(term))

    # === PHASE 3: PROCESSING & SCORING ===
    if not all_linkedin_data and not all_google_data:
        print("❌ No data collected. Exiting.")
        return

    df_clean = data_processor.process_and_merge_data(all_linkedin_data, all_google_data)
    df_scored = data_processor.score_companies(df_clean)
    
    df_scored.to_csv("scored_companies.csv", index=False)
    print("\n💾 Scored company list saved to scored_companies.csv")

    # === PHASE 4: CONTACT ACQUISITION & VALIDATION ===
    top_companies = df_scored[df_scored['likelihood_score'] >= config.LEAD_SCORE_THRESHOLD]
    print(f"\n✨ Found {len(top_companies)} high-potential companies (score >= {config.LEAD_SCORE_THRESHOLD}).")

    final_leads = []
    emails_to_validate = []
    contacts_to_process = []
    
    for _, company in top_companies.iterrows():
        contacts = contact_finder.find_contacts_with_apollo(company['domain'])
        for contact in contacts:
            if contact.get('email'):
                emails_to_validate.append(contact['email'])
                contact.update({'company_name': company['company_name'], 'likelihood_score': company['likelihood_score']})
                contacts_to_process.append(contact)

    if not emails_to_validate:
        print("\n😔 No contacts found for the top companies.")
        return

    validation_results = contact_finder.validate_emails_with_neverbounce(emails_to_validate)
    
    for contact in contacts_to_process:
        if validation_results.get(contact['email']) == 'valid':
            final_leads.append(contact)

    if final_leads:
        df_final = pd.DataFrame(final_leads)[['company_name', 'name', 'title', 'email', 'likelihood_score']]
        df_final.to_csv("final_validated_leads.csv", index=False)
        print(f"\n🎉 Success! Saved {len(df_final)} validated leads to final_validated_leads.csv")
    else:
        print("\n😔 No valid contacts found after validation.")

if __name__ == "__main__":
    main()