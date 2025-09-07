from typing import List, Dict, Any
from . import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, ValidationError

class TargetGroupWithTerms(BaseModel):
    """Target group with rationale and search terms."""
    group_name: str = Field(description="Distinct and specific target customer group name.")
    rationale: str = Field(description="Why this group is a good fit.")
    linkedin_search_terms: List[str] = Field(description="Exactly 5 LinkedIn search terms.")
    google_search_terms: List[str] = Field(description="Exactly 5 Google Places search terms.")

class LeadPlan(BaseModel):
    """Full lead generation plan."""
    targets: List[TargetGroupWithTerms] = Field(
        description="A list of 5-10 target groups with rationale and search terms."
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=config.GEMINI_API_KEY,
    convert_system_message_to_human=True
)

def generate_lead_generation_plan(product_description: str) -> List[Dict[str, Any]]:
    """Generate target groups + search terms for lead generation."""
    print("🤖 Asking Gemini to generate a detailed lead generation plan...")

    structured_llm = llm.with_structured_output(LeadPlan)

    prompt = ChatPromptTemplate.from_messages([
    ("system",
            """You are an expert B2B lead generation strategist and market researcher. 
        Your task is to analyze a product description, identify the most promising customer groups, 
        justify why they are relevant, and generate highly-targeted search terms for LinkedIn and Google Places. 

        Follow these rules strictly:
        - The rationale must be concise (2-3 sentences) and business-focused, 
        explaining why this group is a high-potential customer segment.
        - LinkedIn search terms should be specific keywords or phrases that a recruiter or sales professional 
        would actually use to discover these companies on LinkedIn.
        - Google Places search terms should reflect categories and queries that map directly to the Places API, 
        making it easier to retrieve real businesses.
        - Do not add extra commentary, notes, or formatting outside of the required fields.
        """),
            ("human",
            """
        Analyze the following product description and generate a lead generation plan 
        containing 5-10 distinct target groups. 

        **Product Description:** "{product_description}"

        For each target group, return the following fields:
        1. **group_name** → A short, specific, descriptive name for the group (e.g., "Mid-size HR Consultancies in India").
        2. **rationale** → A clear 2-3 sentence explanation of why this group is a good target for the product.
        3. **linkedin_search_terms** → A list of exactly 5 search phrases optimized for LinkedIn company or people search.
        - Examples: "management consulting firms India", "HR software startups USA".
        4. **google_search_terms** → A list of exactly 5 search phrases optimized for the Google Places API.
        - Examples: "consulting firms near Bangalore", "HR tech companies San Francisco".

        Return your final output in JSON strictly following the schema provided.
        """)
        ])


    chain = prompt | structured_llm

    try:
        response_model = chain.invoke({"product_description": product_description})
    except ValidationError as e:
        print("❌ Schema validation failed:", e)
        return []

    plan_list = []
    for target in response_model.targets:
        # normalize list lengths to exactly 5
        linkedin_terms = (target.linkedin_search_terms or [])[:5]
        google_terms = (target.google_search_terms or [])[:5]

        plan_list.append({
            "group_name": target.group_name,
            "rationale": target.rationale,
            "linkedin_search_terms": linkedin_terms,
            "google_search_terms": google_terms
        })

    print(f"✅ Gemini generated {len(plan_list)} target groups.")
    print(plan_list)
    return plan_list

if __name__ == "__main__":
    product_description = "An AI-powered recruitment automation platform designed to help companies hire faster by screening resumes and scheduling interviews automatically."

    plan = generate_lead_generation_plan(product_description)

    print("\n=== Final Parsed Output ===")
    for group in plan:
        print(f"\nGroup: {group['group_name']}")
        print(f"Rationale: {group['rationale']}")
        print("LinkedIn Terms:", group['linkedin_search_terms'])
        print("Google Terms:", group['google_search_terms'])
