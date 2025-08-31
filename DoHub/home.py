import streamlit as st
from db import register_user, validate_user
from streamlit_cookies_manager import EncryptedCookieManager

# ---- Cookie setup ----
cookies = EncryptedCookieManager(prefix="dohub", password="super-secret-key")
if not cookies.ready():
    st.stop()

st.set_page_config(page_title="DoHub | Home", layout="centered")

# ---- Restore session from cookie ----
if not st.session_state.get("auth") and cookies.get("auth") == "1":
    st.session_state["auth"] = True
    st.session_state["user_email"] = cookies.get("user_email")
    st.session_state["access_token"] = cookies.get("access_token")
    st.session_state["refresh_token"] = cookies.get("refresh_token")

with st.container():
    st.markdown('<div class="__glass-bg-marker"></div>', unsafe_allow_html=True)

    # CSS ... (same glass design as before)

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
                cookies["auth"] = "0"
                cookies.save()
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
                        st.session_state["access_token"] = user["access_token"]
                        st.session_state["refresh_token"] = user["refresh_token"]

                        # Save in cookie
                        cookies["auth"] = "1"
                        cookies["user_email"] = user["email"]
                        cookies["access_token"] = user["access_token"]
                        cookies["refresh_token"] = user["refresh_token"]
                        cookies.save()

                        st.success("Logged in successfully!")
                        st.switch_page("pages/model.py")
                    else:
                        st.error("Invalid email or password.")

            with tab_register:
                new_email = st.text_input("Email", key="reg_email")
                new_pwd = st.text_input("Password", type="password", key="reg_pwd")
                if st.button("Register Volunteer"):
                    if register_user(new_email, new_pwd):
                        st.success("Account created! You can log in now.")
                    else:
                        st.error("Registration failed. Try again.")

    st.markdown('</div>', unsafe_allow_html=True)
