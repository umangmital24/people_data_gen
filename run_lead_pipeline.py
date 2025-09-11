import json
import os
from datetime import datetime

from src.gen_search_terms import generate_lead_generation_plan
from src.scraper import scrape_google_places

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GROUPS_FILE = os.path.join(OUTPUT_DIR, "generated_groups.json")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "companies_results.json")


def run_pipeline(product_description: str):
    # 1️⃣ Generate groups + search terms
    print("🤖 Generating search terms...")
    groups = generate_lead_generation_plan(product_description)

    # Save full group data
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=4)
    print(f"✅ Saved generated groups to {GROUPS_FILE}")

    # 2️⃣ Extract Google search terms only
    all_terms = []
    for group in groups:
        all_terms.extend(group.get("google_search_terms", []))

    print(f"🔎 Total {len(all_terms)} search terms to scrape.")

    # 3️⃣ Load existing results if file exists (for append mode)
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            existing_results = json.load(f)
    else:
        existing_results = []

    # Deduplicate old + new results by place_id
    seen_place_ids = {item["place_id"] for item in existing_results if item.get("place_id")}

    # 4️⃣ Scrape and append results
    for term in all_terms:
        results = scrape_google_places(term)
        for r in results:
            if r.get("place_id") not in seen_place_ids:
                r["search_term"] = term
                r["timestamp"] = datetime.utcnow().isoformat()
                existing_results.append(r)
                seen_place_ids.add(r["place_id"])

    # 5️⃣ Save updated results
    with open(RESULTS_FILE, "w") as f:
        json.dump(existing_results, f, indent=4)

    print(f"✅ Saved {len(existing_results)} unique companies to {RESULTS_FILE}")


if __name__ == "__main__":
    product_description = (
        "An AI-powered recruitment automation platform designed to help companies hire faster by screening resumes and scheduling interviews automatically."
    )
    run_pipeline(product_description)
