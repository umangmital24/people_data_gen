import neverbounce_sdk
from . import config

def verify_email(email):
    """
    Verifies a single email using the NeverBounce API.

    Args:
        email (str): The email address to verify.

    Returns:
        str: The verification result (e.g., 'valid', 'invalid', 'unknown').
    """
    if not email:
        return "not_provided"
    
    # Initialize the NeverBounce client with the API key from config
    nb_client = neverbounce_sdk.client(api_key=config.NEVERBOUNCE_API_KEY)
    
    try:
        resp = nb_client.single_check(email)
        return resp.get('result', 'verification_error')
    except Exception as e:
        print(f"    - NeverBounce Error for {email}: {e}")
        return "verification_error"
