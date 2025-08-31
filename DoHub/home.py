import streamlit as st
from db import register_user, validate_user

st.set_page_config(page_title="DoHub | Home", layout="centered")

# ---- Global page bg ----
st.markdown("""
<style>
html, body, .stApp { background: #0f1115; }
</style>
""", unsafe_allow_html=True)

# ---- Persistent auth (don't reset if already logged in) ----
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

with st.container():
    st.markdown('<div class="__glass-bg-marker"></div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    div:has(> .__glass-bg-marker) {
      position: relative;
      margin: 10vh auto 0 auto;
      width: 90%;
      max-width: 980px;
      padding: 0;
    }
    .__glass-bg-marker {
      position: absolute;
      inset: 0;
      background: rgba(255,255,255,0.07);
      border-radius: 20px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.30);
      border: 1px solid rgba(255,255,255,0.14);
      z-index: 0;
    }
    div:has(> .__glass-bg-marker) > *:not(.__glass-bg-marker) {
      position: relative;
      z-index: 1;
      padding: 2.5rem;
      color: #fff;
    }
    .glass-row { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; }

    /* Restored original title size + spacing */
    .glass-title { 
      font-size: 3.4rem; 
      font-weight: 800; 
      margin: 0 0 1rem 0; 
    }
    .glass-sub { 
      color: #e7e7e7; 
      margin: 0 0 2rem 0; 
      font-size: 1.2rem;
    }

    .stTextInput > div > div {
      background: transparent !important;
      border: 1px solid #555 !important;
      border-radius: 10px !important;
    }
    .stTextInput input { color: #fff !important; }
    .stTextInput input::placeholder { color: #9aa0a6 !important; }
    .stButton > button {
      background: #ffffff22; color: #fff; border: 1px solid #555;
      padding: 10px 16px; border-radius: 12px; font-weight: 600;
    }
    .stButton > button:hover { background: #ffffff33; }
    label { color: #ddd !important; }
    hr.glass-sep { border: none; border-top: 1px solid #333; margin: 1.2rem 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-row">', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.1, 1], gap="large")
    with left_col:
        st.markdown('<div class="glass-title">Welcome to DoHub</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-sub">Connecting volunteers with NGOs across India.</div>', unsafe_allow_html=True)

        if st.button("Sign Up as NGO"):
            st.switch_page("pages/ngoscreen.py")

        if st.session_state.get("auth"):
            st.success(f"Logged in as {st.session_state.get('user_email')}")
            if st.button("Go to Profile"):
                st.switch_page("pages/profile.py")
            if st.button("Log Out"):
                st.session_state.clear()
                st.rerun()

    with right_col:
        if not st.session_state.get("auth"):
            tab_login, tab_register = st.tabs(["Log In", "Register"])
            with tab_login:
                email = st.text_input("Email", placeholder="you@example.org", key="login_email")
                pwd = st.text_input("Password", type="password", placeholder="Enter password", key="login_pwd")
                if st.button("Log In"):
                    user = validate_user(email, pwd)
                    if user:
                        st.session_state["auth"] = True
                        st.session_state["user_email"] = user["email"]
                        st.session_state["role"] = user["role"]
                        st.success("Logged in successfully!")
                        st.switch_page("pages/model.py")
                    else:
                        st.error("Invalid email or password.")
            with tab_register:
                new_email = st.text_input("Email", key="reg_email")
                new_pwd = st.text_input("Password", type="password", key="reg_pwd")
                if st.button("Register Volunteer"):
                    if register_user(new_email, new_pwd, role="volunteer"):
                        st.success("Account created! You can log in now.")
                    else:
                        st.error("Registration failed. Email may already exist.")

    st.markdown('</div>', unsafe_allow_html=True)
