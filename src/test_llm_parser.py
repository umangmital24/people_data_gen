from src.llm_handler import generate_lead_generation_plan

if __name__ == "__main__":
    product_description = "An AI-powered recruitment automation platform designed to help companies hire faster by screening resumes and scheduling interviews automatically."

    plan = generate_lead_generation_plan(product_description)

    print("\n=== Final Parsed Output ===")
    for group in plan:
        print(f"\nGroup: {group['group_name']}")
        print(f"Rationale: {group['rationale']}")
        print("LinkedIn Terms:", group['linkedin_search_terms'])
        print("Google Terms:", group['google_search_terms'])
