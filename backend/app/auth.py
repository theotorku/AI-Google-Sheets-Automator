import os
from supabase import create_client, Client
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use Service Role for admin tasks if needed, or Anon for client

if not SUPABASE_URL or not SUPABASE_KEY:
    # Fallback for dev/test without env
    print("Warning: Supabase credentials not found in env.")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies the Bearer token using Supabase Auth.
    Returns the user object if valid.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    token = credentials.credentials
    try:
        # Get the user associated with the token
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_response.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
