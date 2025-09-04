import os
import json
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# -----------------------------
# 1. Setup HuggingFace Endpoint
# -----------------------------
# Ensure your Hugging Face API token is set as an environment variable.
# For example: export HUGGINGFACE_API_TOKEN='your_hf_token_here'
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

if not HUGGINGFACE_API_TOKEN:
    raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set.")

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    temperature=0.6,
    max_new_tokens=512,
)

# -----------------------------
# 2. Define Pydantic Schemas for Structured Output
# -----------------------------
class TargetGroup(BaseModel):
    """Defines the structure for a single target customer group."""
    group_name: str = Field(description="Name of the target group")
    rationale: str = Field(description="Rationale behind selecting this group")

class TargetGroupsResponse(BaseModel):
    """Defines the structure for the list of all target groups."""
    groups: list[TargetGroup] = Field(description="List of customer groups")

class SearchTermsResponse(BaseModel):
    """Defines the structure for the search terms response."""
    linkedin_terms: list[str] = Field(description="Search terms for LinkedIn")
    google_terms: list[str] = Field(description="Search terms for Google Places")

# -----------------------------
# 3. Define Prompt Templates
# -----------------------------
target_group_prompt = PromptTemplate(
    template="""[INST] Based on the following product description, generate 3 distinct and specific target customer groups.
Product: "{product_desc}"

For each group, provide a name and a brief rationale.
Return the output as a valid JSON object following this schema:
{format_instructions}[/INST]""",
    input_variables=["product_desc"],
    partial_variables={"format_instructions": JsonOutputParser(pydantic_object=TargetGroupsResponse).get_format_instructions()}
)

search_terms_prompt = PromptTemplate(
    template="""[INST] For the target group "{group_name}" with the rationale "{rationale}", generate search terms for scraping data.

Provide 5 terms for LinkedIn company search and 5 terms for Google Places search.
Return the output as a valid JSON object with the following schema:
{format_instructions}[/INST]""",
    input_variables=["group_name", "rationale"],
    partial_variables={"format_instructions": JsonOutputParser(pydantic_object=SearchTermsResponse).get_format_instructions()}
)

# -----------------------------
# 4. Create Processing Chains
# -----------------------------
# This chain takes a product description, sends it to the LLM, and parses the output into the TargetGroupsResponse schema.
target_groups_chain = target_group_prompt | llm | JsonOutputParser(pydantic_object=TargetGroupsResponse)

# This chain takes a group name and rationale, sends it to the LLM, and parses the output into the SearchTermsResponse schema.
search_terms_chain = search_terms_prompt | llm | JsonOutputParser(pydantic_object=SearchTermsResponse)

# -----------------------------
# 5. Main Execution Function
# -----------------------------
def run_analysis():
    """Executes the full analysis pipeline: getting groups and then search terms."""
    print("--- Starting LangChain Hugging Face Analysis ---")

    product_description = (
        "A sustainable, direct-trade coffee subscription box that delivers freshly roasted, "
        "single-origin beans to your door every month. We focus on ethical sourcing and "
        "unique flavor profiles from around the world."
    )

    print(f"\nProduct: {product_description}\n")

    # Phase 1: Get Target Groups
    try:
        print("🤖 Phase 1: Asking LLM for target groups...")
        # The .invoke method runs the chain with the given input.
        target_groups_resp = target_groups_chain.invoke({"product_desc": product_description})
        groups = target_groups_resp['groups']
        print(f"✅ LLM identified {len(groups)} target groups.")
        print("\n--- Identified Target Groups ---")
        for i, g in enumerate(groups):
            print(f"{i+1}. {g['group_name']} -> {g['rationale']}")
        print("--------------------------------\n")
    except Exception as e:
        print(f"❌ Error getting target groups: {e}")
        return

    # Phase 2: Get Search Terms for the First Group
    if groups:
        first_group = groups[0]
        try:
            print(f"🧠 Asking LLM for search terms for: '{first_group['group_name']}'...")
            search_terms_resp = search_terms_chain.invoke({
                "group_name": first_group['group_name'],
                "rationale": first_group['rationale']
            })
            print("✅ LLM generated search terms.")
            print(f"\n--- Search Terms for '{first_group['group_name']}' ---")
            print("LinkedIn Terms:", search_terms_resp['linkedin_terms'])
            print("Google Terms:  ", search_terms_resp['google_terms'])
            print("--------------------------------------\n")
        except Exception as e:
            print(f"❌ Error getting search terms: {e}")

    print("--- Analysis Complete ---")


if __name__ == "__main__":
    run_analysis()

