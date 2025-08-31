import streamlit as st
import sys
from pathlib import Path

# --- DB imports (now Firebase, no sqlite) ---
ROOT = Path(__file__).resolve().parent
if (ROOT / "db.py").exists():
    sys.path.append(str(ROOT))
elif (ROOT.parent / "db.py").exists():
    sys.path.append(str(ROOT.parent))

from db import validate_user, register_user   # ✅ Firebase functions (no init_db)

st.set_page_config(page_title="DoHub | Home", layout="centered")

# ---- Global page bg (keep your dark theme) ----
st.markdown("""
<style>
html, body, .stApp { background: #0f1115; }
</style>
""", unsafe_allow_html=True)

# ================== GLASS CARD (that actually contains widgets) ==================
with st.container():
    st.markdown('<div class="__glass-bg-marker"></div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* (your existing CSS unchanged) */
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-row">', unsafe_allow_html=True)

    # LEFT SIDE
    left_col, right_col = st.columns([1.1, 1], gap="large")
    with left_col:
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

    # RIGHT SIDE
    with right_col:
        if not st.session_state.get("auth"):
            tab_login, tab_register = st.tabs(["Log In", "Register"])

            # ---- Log In ----
            with tab_login:
                email = st.text_input("Email", placeholder="you@example.org", key="login_email")
                pwd = st.text_input("Password", type="password", placeholder="Enter password", key="login_pwd")
                if st.button("Log In", key="login_btn"):
                    user = validate_user(email, pwd)  # ✅ Firebase REST API
                    if user:
                        st.session_state["auth"] = True
                        st.session_state["user_email"] = user["email"]
                        st.session_state["role"] = user.get("role", "volunteer")
                        st.success("Logged in successfully!")
                        st.switch_page("pages/model.py")
                    else:
                        st.error("Invalid email or password.")

            # ---- Register ----
            with tab_register:
                new_email = st.text_input("Email", key="reg_email")
                new_pwd = st.text_input("Password", type="password", key="reg_pwd")
                if st.button("Register Volunteer", key="reg_btn"):
                    if not new_email or not new_pwd:
                        st.error("Enter email and password to register.")
                    else:
                        ok = register_user(new_email, new_pwd, role="volunteer")  # ✅ Firebase create
                        if ok:
                            st.success("Account created! You can log in now.")
                        else:
                            st.error("This email is already registered.")

    st.markdown('</div>', unsafe_allow_html=True)
