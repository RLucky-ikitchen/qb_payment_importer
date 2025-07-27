import os
import json
from urllib.parse import urlencode
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
from quickbooks import QuickBooks

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REALM_ID = os.getenv("REALM_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")

AUTH_BASE_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
SCOPE = [
    "com.intuit.quickbooks.accounting"
]
TOKEN_FILE = ".qb_token.json"

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
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url, _ = oauth.authorization_url(AUTH_BASE_URL)
    return auth_url

def exchange_code_for_token(code):
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    try:
        token = oauth.fetch_token(
            TOKEN_URL,
            code=code,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            include_client_id=True
        )
        save_token(token)
        return True
    except Exception as e:
        print(f"Token exchange failed: {e}")
        return False

def get_qb_client():
    token = load_token()
    if not token:
        raise Exception("Not authenticated with QuickBooks.")
    qb_client = QuickBooks(
        sandbox=(ENVIRONMENT == "sandbox"),
        consumer_key=CLIENT_ID,
        consumer_secret=CLIENT_SECRET,
        access_token=token["access_token"],
        refresh_token=token.get("refresh_token"),
        company_id=REALM_ID,
        callback_url=REDIRECT_URI
    )
    return qb_client
