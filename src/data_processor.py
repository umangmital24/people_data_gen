# src/data_processor.py
import pandas as pd
from urllib.parse import urlparse
from . import config

def _get_domain(url):
    """Helper function to extract the domain from a URL string."""
    if not isinstance(url, str) or not url.startswith('http'):
        return None
    try:
        return urlparse(url).netloc.replace('www.', '').lower()
    except:
        return None

def process_and_merge_data(linkedin_data, google_data):
    """Cleans, merges, and deduplicates data from both sources."""
    print("🧹 Cleaning and merging data...")
    df_linkedin = pd.DataFrame(linkedin_data)
    df_google = pd.DataFrame(google_data)

    df_linkedin.rename(columns={'employees': 'employee_count'}, inplace=True)
    df_linkedin['domain'] = df_linkedin['website'].apply(_get_domain)
    df_google['domain'] = df_google['website'].apply(_get_domain)

    df_merged = pd.merge(df_linkedin, df_google, on='domain', how='outer', suffixes=('_linkedin', '_google'))
    df_merged['company_name'] = df_merged['name_linkedin'].fillna(df_merged['name_google'])
    df_merged['website'] = df_merged['website_linkedin'].fillna(df_merged['website_google'])
    
    df_merged.dropna(subset=['company_name', 'domain'], inplace=True)
    df_merged.drop_duplicates(subset=['domain'], keep='first', inplace=True)

    final_cols = ['company_name', 'domain', 'website', 'industry', 'employee_count', 'address']
    for col in final_cols:
        if col not in df_merged.columns: df_merged[col] = None
    return df_merged[final_cols]

def score_companies(df):
    """Applies a scoring model to the cleaned company data."""
    print("⚖️ Scoring companies...")
    
    def calculate_score(row):
        emp_score = 0
        emp_count = row.get('employee_count')
        if pd.notna(emp_count):
            if 50 <= emp_count <= 750: emp_score = 10
            elif 25 <= emp_count < 50 or 750 < emp_count <= 1500: emp_score = 5

        industry_score = 0
        industry = str(row.get('industry', '')).lower()
        if any(kw in industry for kw in ['manufacturing', 'industrial', 'machinery', 'automotive']): industry_score = 10
        elif 'technology' in industry: industry_score = 3
            
        final_score = (config.SCORING_WEIGHTS['employee_count'] * emp_score) + \
                      (config.SCORING_WEIGHTS['industry'] * industry_score)
        return round(final_score, 2)

    df['likelihood_score'] = df.apply(calculate_score, axis=1)
    return df.sort_values(by='likelihood_score', ascending=False)