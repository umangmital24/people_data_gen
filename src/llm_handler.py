import json
import requests
from . import config

# You can swap this with other instruction-tuned models on Hugging Face Hub
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

# Prepare the authorization headers
HEADERS = {
    "Authorization": f"Bearer {config.HUGGINGFACE_API_TOKEN}"
}

def _query_huggingface_api(payload):
    """Generic function to query the Hugging Face Inference API."""
    response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return response.json()

def _clean_json_response(response_text, prompt):
    """
    Cleans the model's response to extract a valid JSON string.
    Hugging Face models often return the prompt plus the generated text.
    """
    # Remove the prompt from the response to isolate the generated text
    if prompt in response_text:
        response_text = response_text.replace(prompt, "").strip()

    # Find the start and end of the JSON object
    json_start = response_text.find('{')
    json_end = response_text.rfind('}')

    if json_start != -1 and json_end != -1:
        json_str = response_text[json_start : json_end + 1]
        try:
            # Attempt to parse the extracted string as JSON
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON. Reason: {e}")
            print(f"Raw string attempted to parse: {json_str}")
            return None
    else:
        print("Error: Could not find a valid JSON object in the model's response.")
        print(f"Raw response received: {response_text}")
        return None

def get_target_groups(product_desc):
    """Gets target customer groups from a Hugging Face LLM in a structured JSON format."""
    print("🤖 Phase 1: Asking HF LLM for target groups...")
    # Using [INST] tags is a common convention for instruction-tuned models like Mixtral
    prompt = f"""[INST] Based on the following product description, generate 3 distinct and specific target customer groups.
Product: "{product_desc}"

For each group, provide a name and a brief rationale.
Return the output as a valid JSON array of objects inside a root key "groups".
IMPORTANT: Your response MUST be ONLY the JSON object, with no other text, explanation, or markdown formatting.
{{
    "groups": [
        {{"group_name": "...", "rationale": "..."}}
    ]
}}[/INST]"""

    try:
        api_response = _query_huggingface_api({
            "inputs": prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.6}
        })
        
        raw_text = api_response[0]['generated_text']
        json_response = _clean_json_response(raw_text, prompt)

        if json_response and "groups" in json_response:
            groups = json_response.get("groups", [])
            print(f"✅ LLM identified {len(groups)} target groups.")
            return groups
        else:
            print("❌ Failed to parse groups from the LLM response.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return []

def get_search_terms(target_group):
    """Gets search terms for a specific target group from a Hugging Face LLM."""
    print(f"🧠 Asking HF LLM for search terms for: '{target_group['group_name']}'...")
    prompt = f"""[INST] For the target group "{target_group['group_name']}" with the rationale "{target_group['rationale']}", generate search terms for scraping data.

Provide 5 terms for LinkedIn company search and 5 terms for Google Places search.
Return the output as a valid JSON object.
IMPORTANT: Your response MUST be ONLY the JSON object, with no other text, explanation, or markdown formatting.
{{
    "linkedin_terms": ["...", "..."],
    "google_terms": ["...", "..."]
}}[/INST]"""

    try:
        api_response = _query_huggingface_api({
            "inputs": prompt,
            "parameters": {"max_new_tokens": 256, "temperature": 0.6}
        })
        
        raw_text = api_response[0]['generated_text']
        json_response = _clean_json_response(raw_text, prompt)
        
        if json_response:
             print("✅ LLM generated search terms.")
             return json_response
        else:
            print("❌ Failed to parse search terms from the LLM response.")
            return {"linkedin_terms": [], "google_terms": []}
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {"linkedin_terms": [], "google_terms": []}
