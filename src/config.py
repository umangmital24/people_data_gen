# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
NEVERBOUNCE_API_KEY = os.getenv("NEVERBOUNCE_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_TOKEN = "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"

# --- Pipeline Settings ---
PRODUCT_DESCRIPTION = "An AI-powered platform that automates ESG (Environmental, Social, and Governance) compliance reporting for mid-sized manufacturing companies (50-750 employees). It saves time, reduces audit risk, and helps companies improve their sustainability scores."
LEAD_SCORE_THRESHOLD = 7.0 # Minimum score to qualify for contact search
CONTACT_PERSONAS = ["Head of Sustainability", "Compliance Officer", "Chief Financial Officer", "VP of Operations"]

# Scoring Weights (must add up to 1.0)
SCORING_WEIGHTS = {
    "employee_count": 0.5,
    "industry": 0.5
}