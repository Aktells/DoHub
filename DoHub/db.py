import os
from supabase import create_client
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv()

@st.cache_resource
def init_supabase():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

def register_user(email: str, password: str) -> bool:
    """Register a new user with Supabase Auth"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            print("✅ Registered:", response.user.email)
            return True
        if response.error:
            print("❌ Registration error:", response.error.message)
        return False
    except Exception as e:
        print("❌ Exception during register:", e)
        return False

def validate_user(email: str, password: str):
    """Log in user with Supabase Auth"""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print("DEBUG LOGIN RESPONSE:", response)  # log full response

        if response.session and response.user:
            return {
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }

        if response.error:
            print("❌ Login error:", response.error.message)
        return None
    except Exception as e:
        print("❌ Exception during login:", e)
        return None
