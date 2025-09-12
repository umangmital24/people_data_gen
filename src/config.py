import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
NEVERBOUNCE_API_KEY = os.getenv("NEVERBOUNCE_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN") # Note: This token is not currently used but is kept for future expansion.
# --- LLM & Ollama Settings ---
# Example: http://localhost:11434 if running Ollama locally
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- Pipeline Settings ---
PRODUCT_DESCRIPTION = "An AI-powered platform that automates ESG (Environmental, Social, and Governance) compliance reporting for mid-sized manufacturing companies (50-750 employees). It saves time, reduces audit risk, and helps companies improve their sustainability scores."
LEAD_SCORE_THRESHOLD = 7.0
CONTACT_PERSONAS = ["Head of Sustainability", "Compliance Officer", "Chief Financial Officer", "VP of Operations"]
SCORING_WEIGHTS = {
    "employee_count": 0.5,
    "industry": 0.5
}

# --- File Paths ---
output_dir = "output"
linkedin_data_file = os.path.join(output_dir, "LinkedIn_company_information.json")
google_places_data_file = os.path.join(output_dir, "companies.json")
merged_data_file = os.path.join(output_dir, "final_merged_companies.json")
verified_employees_file = os.path.join(output_dir, "verified_employees.json")
lead_plan_file = os.path.join(output_dir, "lead_plan.json")

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Filters for Data Processor ---
industry_filter = "Information Technology & Services"
country_filter = "IN"
