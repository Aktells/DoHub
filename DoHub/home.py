import streamlit as st
# --- imports for DB (place at the very top of home.py) ---
import sys
from pathlib import Path

# If your app files live in DoHub/, adjust root accordingly.
ROOT = Path(__file__).resolve().parent
if (ROOT / "db.py").exists():
    sys.path.append(str(ROOT))
elif (ROOT.parent / "db.py").exists():
    sys.path.append(str(ROOT.parent))

from db import init_db, validate_user, register_user, seed_demo_user

init_db()

st.set_page_config(page_title="DoHub | Home", layout="centered")

# ---- Global page bg (keep your dark theme) ----
st.markdown("""
<style>
html, body, .stApp { background: #0f1115; }
</style>
""", unsafe_allow_html=True)

# ================== GLASS CARD (that actually contains widgets) ==================
with st.container():  # this is the real container that holds widgets
    # 1) add a background layer and a marker class
    st.markdown('<div class="__glass-bg-marker"></div>', unsafe_allow_html=True)

    # 2) styles that turn THIS container into a glass card
    st.markdown("""
    <style>
    /* Find any Streamlit container that has our marker inside */
    div:has(> .__glass-bg-marker) {
      position: relative;
      margin: 10vh auto 0 auto;     /* center vertically a bit */
      width: 90%;
      max-width: 980px;             /* same width as your design */
      padding: 0;                   /* we'll pad content layer, not wrapper */
    }

    /* The glass background layer that fills the container */
    .__glass-bg-marker {
      position: absolute;
      inset: 0;                     /* top/right/bottom/left = 0 */
      background: rgba(255,255,255,0.07);
      border-radius: 20px;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.30);
      border: 1px solid rgba(255,255,255,0.14);
      z-index: 0;                   /* sits behind widgets */
    }

    /* Put ALL widgets on top + give inner padding like a card */
    div:has(> .__glass-bg-marker) > *:not(.__glass-bg-marker) {
      position: relative;
      z-index: 1;
      padding: 2.5rem;              /* inner padding */
      color: #fff;
    }

    /* two-column layout spacing inside card */
    .glass-row { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; }
    .glass-title { font-size: 2.2rem; font-weight: 800; margin: 0 0 .4rem 0; }
    .glass-sub { color: #e7e7e7; margin: 0 0 1.1rem 0; }

    /* inputs + buttons styling to match card */
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

    # 3) the actual content INSIDE the card
    st.markdown('<div class="glass-row">', unsafe_allow_html=True)

    # LEFT SIDE
    left_col, right_col = st.columns([1.1, 1], gap="large")
    with left_col:
        st.markdown('<div class="glass-title">Welcome to DoHub</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-sub">Connecting volunteers with NGOs across India.</div>',
                    unsafe_allow_html=True)

        # NGO signup goes to the dedicated NGO screen (no auth needed)
        if st.button("Sign Up as NGO"):
            st.switch_page("pages/ngoscreen.py")

        # If already logged in, show quick actions (optional)
        if st.session_state.get("auth"):
            st.success(f"Logged in as {st.session_state.get('user_email')}")
            if st.button("Go to Profile"):
                st.switch_page("pages/profile.py")
            if st.button("Log Out"):
                st.session_state.clear()
                st.rerun()
# ---------- RIGHT: Animated Login / Register ----------
# CSS for the small fade/slide animation
st.markdown("""
<style>
.fade-enter { animation: fadeSlide .35s ease both; }
@keyframes fadeSlide {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.auth-tabs a {
  margin-right: 10px; font-weight: 700; text-decoration: none;
  padding: 6px 10px; border-radius: 10px; border: 1px solid #555;
  background: #ffffff1a; color: #fff;
}
.auth-tabs a.active { background: #ffffff33; }
.auth-tabs a:hover { background: #ffffff3f; }
</style>
""", unsafe_allow_html=True)

# Keep a tiny state to know which pane to show
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def _switch_auth(mode: str):
    st.session_state.auth_mode = mode

with right:
    # Header "tabs" that look like your OG controls
    col_tab_login, col_tab_reg = st.columns([1,1])
    with col_tab_login:
        if st.button("Log In", key="tab_login_btn"):
            _switch_auth("login")
    with col_tab_reg:
        if st.button("Register", key="tab_register_btn"):
            _switch_auth("register")

    # LOGIN PANE
    if st.session_state.auth_mode == "login" and not st.session_state.get("auth", False):
        st.markdown('<div class="fade-enter">', unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="you@example.org", key="login_email")
        pwd   = st.text_input("Password", type="password", placeholder="Enter password", key="login_pwd")
        if st.button("Log In", key="login_btn"):
            user = validate_user(email, pwd)   # <-- real DB check
            if user:
                st.session_state["auth"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["role"] = user["role"]
                st.success("Logged in successfully!")
                st.switch_page("pages/model.py")
            else:
                st.error("Invalid email or password.")
        st.markdown('</div>', unsafe_allow_html=True)

    # REGISTER PANE
    elif st.session_state.auth_mode == "register" and not st.session_state.get("auth", False):
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

    # When already logged in
    elif st.session_state.get("auth", False):
        st.markdown('<div class="fade-enter">', unsafe_allow_html=True)
        st.success(f"Logged in as {st.session_state['user_email']} ({st.session_state.get('role','')})")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Go to Profile"):
                st.switch_page("pages/profile.py")
        with c2:
            if st.button("Log Out"):
                st.session_state.clear()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


