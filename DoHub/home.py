import streamlit as st
# --- imports for DB ---
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if (ROOT / "db.py").exists():
    sys.path.append(str(ROOT))
elif (ROOT.parent / "db.py").exists():
    sys.path.append(str(ROOT.parent))

from db import init_db, validate_user, register_user, seed_demo_user
init_db()
seed_demo_user()  # optional demo user

st.set_page_config(page_title="DoHub | Home", layout="centered")

# ---- Page background ----
st.markdown("""
<style>
html, body, .stApp { background: #0f1115; }
</style>
""", unsafe_allow_html=True)

# ================== GLASS CARD ==================
with st.container():
    st.markdown('<div class="__glass-bg-marker"></div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    div:has(> .__glass-bg-marker) {
      position: relative; margin: 10vh auto 0 auto;
      width: 90%; max-width: 980px; padding: 0;
    }
    .__glass-bg-marker {
      position: absolute; inset: 0;
      background: rgba(255,255,255,0.07);
      border-radius: 20px;
      backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.30);
      border: 1px solid rgba(255,255,255,0.14);
      z-index: 0;
    }
    div:has(> .__glass-bg-marker) > *:not(.__glass-bg-marker) {
      position: relative; z-index: 1; padding: 2.5rem; color: #fff;
    }
    .glass-title { font-size: 2.2rem; font-weight: 800; margin: 0 0 .4rem 0; }
    .glass-sub { color: #e7e7e7; margin: 0 0 1.1rem 0; }
    .stTextInput > div > div {
      background: transparent !important; border: 1px solid #555 !important; border-radius: 10px !important;
    }
    .stTextInput input { color: #fff !important; }
    .stTextInput input::placeholder { color: #9aa0a6 !important; }
    .stButton > button {
      background: #ffffff22; color: #fff; border: 1px solid #555;
      padding: 10px 16px; border-radius: 12px; font-weight: 600;
    }
    .stButton > button:hover { background: #ffffff33; }
    label { color: #ddd !important; }
    </style>
    """, unsafe_allow_html=True)

    # === two columns inside card ===
    left, right = st.columns([1.1, 1], gap="large")

    # LEFT SIDE
    with left:
        st.markdown('<div class="glass-title">Welcome to DoHub</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-sub">Connecting volunteers with NGOs across India.</div>',
                    unsafe_allow_html=True)

        if st.button("Sign Up as NGO"):
            st.switch_page("pages/ngoscreen.py")

        if st.session_state.get("auth"):
            st.success(f"Logged in as {st.session_state.get('user_email')}")
            if st.button("Go to Profile"):
                st.switch_page("pages/profile.py")
            if st.button("Log Out"):
                st.session_state.clear()
                st.rerun()

    # RIGHT SIDE (animated login/register)
    with right:
        st.markdown("""
        <style>
        .fade-enter { animation: fadeSlide .35s ease both; }
        @keyframes fadeSlide { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }
        </style>
        """, unsafe_allow_html=True)

        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        def _switch_auth(mode: str):
            st.session_state.auth_mode = mode

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log In", key="tab_login_btn"):
                _switch_auth("login")
        with c2:
            if st.button("Register", key="tab_register_btn"):
                _switch_auth("register")

        if st.session_state.get("auth"):
            st.markdown('<div class="fade-enter">', unsafe_allow_html=True)
            st.success(f"Logged in as {st.session_state['user_email']} ({st.session_state.get('role','')})")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Go to Profile"):
                    st.switch_page("pages/profile.py")
            with b2:
                if st.button("Log Out"):
                    st.session_state.clear()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.auth_mode == "login":
            st.markdown('<div class="fade-enter">', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.org", key="login_email")
            pwd   = st.text_input("Password", type="password", placeholder="Enter password", key="login_pwd")
            if st.button("Log In", key="login_btn"):
                user = validate_user(email, pwd)
                if user:
                    st.session_state["auth"] = True
                    st.session_state["user_email"] = user["email"]
                    st.session_state["role"] = user["role"]
                    st.success("Logged in successfully!")
                    st.switch_page("pages/model.py")
                else:
                    st.error("Invalid email or password.")
            st.markdown('</div>', unsafe_allow_html=True)

        else:  # register
            st.markdown('<div class="fade-enter">', unsafe_allow_html=True)
            new_email = st.text_input("Email", key="reg_email")
            new_pwd   = st.text_input("Password", type="password", key="reg_pwd")
            if st.button("Create Account", key="reg_btn"):
                if not new_email or not new_pwd:
                    st.error("Please enter email and password.")
                else:
                    ok = register_user(new_email, new_pwd, role="volunteer")
                    if ok:
                        st.success("Account created! Please log in.")
                        _switch_auth("login")
                    else:
                        st.error("This email is already registered.")
            st.markdown('</div>', unsafe_allow_html=True)
