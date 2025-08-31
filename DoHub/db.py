from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"❌ Missing Supabase config. Got URL={SUPABASE_URL}, KEY={SUPABASE_KEY}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return True if response.user else False
    except Exception as e:
        print("Register failed:", e)
        return False

def validate_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            return {
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        return None
    except Exception as e:
        print("Login failed:", e)
        return None
