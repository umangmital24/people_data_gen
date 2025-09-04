# src/llm_handler.py
import json
from openai import OpenAI
from . import config

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

def get_target_groups(product_desc):
    """Gets target customer groups from an LLM in a structured JSON format."""
    print("🤖 Phase 1: Asking LLM for target groups...")
    prompt = f"""
    Based on the following product description, generate 3 distinct and specific target customer groups.
    Product: "{product_desc}"

    For each group, provide a name and a brief rationale.
    Return the output as a valid JSON array of objects inside a root key "groups", like this:
    {{
        "groups": [
            {{"group_name": "...", "rationale": "..."}},
            {{"group_name": "...", "rationale": "..."}}
        ]
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    json_response = json.loads(response.choices[0].message.content)
    groups = json_response.get("groups", [])
    print(f"✅ LLM identified {len(groups)} target groups.")
    return groups

def get_search_terms(target_group):
    """Gets search terms for a specific target group from an LLM."""
    print(f"🧠 Asking LLM for search terms for: '{target_group['group_name']}'...")
    prompt = f"""
    For the target group "{target_group['group_name']}" with the rationale "{target_group['rationale']}",
    generate specific search terms for scraping data.

    Provide 5 terms for LinkedIn company search and 5 terms for Google Places search.
    Return the output as a valid JSON object, like this:
    {{
        "linkedin_terms": ["...", "..."],
        "google_terms": ["...", "..."]
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    return json.loads(response.choices[0].message.content)