import os
import json
from urllib.parse import urlencode
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REALM_ID = os.getenv("REALM_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")

TOKEN_FILE = ".qb_token.json"

# Initialize AuthClient
def get_auth_client():
    if ENVIRONMENT == "sandbox":
        auth_client = AuthClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            environment=ENVIRONMENT,
            redirect_uri=REDIRECT_URI,
        )
    else:
        auth_client = AuthClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            environment=ENVIRONMENT,
            redirect_uri=REDIRECT_URI,
        )
    return auth_client

# Helper: Save/load token locally
def save_token(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def is_authenticated():
    token = load_token()
    return token is not None and "access_token" in token

def get_qb_auth_url():
    auth_client = get_auth_client()
    scopes = [
        Scopes.ACCOUNTING,
    ]
    auth_url = auth_client.get_authorization_url(scopes)
    return auth_url

def exchange_code_for_token(code):
    try:
        auth_client = get_auth_client()
        auth_client.get_bearer_token(code, realm_id=REALM_ID)
        
        # Save token data
        token_data = {
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "token_type": "bearer",
            "expires_in": auth_client.expires_in,
            "realm_id": REALM_ID,
            "environment": ENVIRONMENT
        }
        save_token(token_data)
        return True
    except Exception as e:
        print(f"Token exchange failed: {str(e)}")
        return False

def get_qb_client():
    token_data = load_token()
    if not token_data:
        raise Exception("Not authenticated with QuickBooks.")
    
    # Initialize QuickBooks client with proper authentication
    auth_client = get_auth_client()
    auth_client.access_token = token_data.get("access_token")
    auth_client.refresh_token = token_data.get("refresh_token")
    
    try:
        qb = QuickBooks(
            auth_client=auth_client,
            refresh_token=token_data.get("refresh_token"),
            company_id=token_data.get("realm_id"),
            sandbox=(ENVIRONMENT == "sandbox")
        )
        return qb
    except Exception as e:
        raise Exception(f"Failed to initialize QuickBooks client: {str(e)}")
