import os
from supabase import create_client
from dotenv import load_dotenv
import streamlit as st

# Load env vars
load_dotenv()

@st.cache_resource  # cache Supabase client as a resource
def init_supabase():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

def register_user(email, password):
    """Register a new user with Supabase Auth"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if getattr(response, "user", None):
            return True
        return False
    except Exception as e:
        print("Register failed:", e)
        return False

def validate_user(email, password):
    """Log in user with Supabase Auth (v2 style)"""
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        # DEBUG: print the whole response to terminal
        print("DEBUG LOGIN RESPONSE:", response)

        # Check if login succeeded
        if response.session and response.user:
            return {
                "email": response.user.email,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }

        # If we get here, login failed → print reason
        if hasattr(response, "error") and response.error:
            print("Supabase login error:", response.error.message)

        return None
    except Exception as e:
        print("Login failed with exception:", e)
        return None
with tab_login:
    email = st.text_input("Email", placeholder="you@example.org", key="login_email")
    pwd = st.text_input("Password", type="password", placeholder="Enter password", key="login_pwd")

    if st.button("Log In"):
        print("DEBUG: Login button clicked with", email, pwd)  # 👈 see if button fires

        user = validate_user(email, pwd)

        print("DEBUG: validate_user returned", user)  # 👈 see what came back

        if user:
            st.session_state["auth"] = True
            st.session_state["user_email"] = user["email"]
            st.session_state["access_token"] = user["access_token"]
            st.session_state["refresh_token"] = user["refresh_token"]

            st.success("Logged in successfully!")
            st.switch_page("pages/model.py")
        else:
            st.error("Invalid email or password.")




