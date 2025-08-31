
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fzklrmnfnvnwiypgomgq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # keep secret!
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_user(email, password):
    """Register a new user with Supabase Auth"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return True
        else:
            print("Signup error:", response)
            return False
    except Exception as e:
        print("Register failed:", e)
        return False

def validate_user(email, password):
    """Log in user and return session + user info"""
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

def get_current_user():
    """Restore logged-in session if exists"""
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            return {"email": session.user.email}
        return None
    except Exception as e:
        print("Get session failed:", e)
        return None
