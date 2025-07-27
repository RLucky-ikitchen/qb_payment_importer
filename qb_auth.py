import os
import json
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REALM_ID = os.getenv("REALM_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")

TOKEN_FILE = ".qb_token.json"

# Mock QuickBooks client
class MockQuickBooksClient:
    def __init__(self):
        self.authenticated = True
        self.company_id = REALM_ID

# Helper: Save/load token locally (for demo)
def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def is_authenticated():
    token = load_token()
    return token is not None and "access_token" in token

def get_qb_auth_url():
    # Mock auth URL - replace with actual OAuth implementation
    base_url = "https://appcenter.intuit.com/connect/oauth2"
    params = {
        "client_id": CLIENT_ID or "mock_client_id",
        "response_type": "code",
        "scope": "com.intuit.quickbooks.accounting",
        "redirect_uri": REDIRECT_URI or "http://localhost:8501",
        "state": "test_state"
    }
    return f"{base_url}?{urlencode(params)}"

def exchange_code_for_token(code):
    # Mock token exchange - replace with actual OAuth implementation
    try:
        mock_token = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_type": "bearer",
            "expires_in": 3600
        }
        save_token(mock_token)
        return True
    except Exception as e:
        print(f"Token exchange failed: {e}")
        return False

def get_qb_client():
    token = load_token()
    if not token:
        raise Exception("Not authenticated with QuickBooks.")
    # Return mock client - replace with actual QuickBooks SDK client
    return MockQuickBooksClient()
