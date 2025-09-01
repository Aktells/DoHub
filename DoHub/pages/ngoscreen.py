import streamlit as st
import re
import sys
from pathlib import Path

# Ensure root is importable for db.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from db import register_user, supabase  # use Supabase client + register_user

# ---------- OPTIONAL: email notify ----------
import smtplib
from email.mime.text import MIMEText

ADMIN_EMAIL = "apoorvkh18@gmail.com"      # <-- CHANGE
SMTP_SERVER = "smtp.gmail.com"            # Gmail
SMTP_PORT   = 587
SMTP_USER   = "apoorvkh18@gmail.com"      # <-- CHANGE
SMTP_PASS   = "cebw vbgh mnds xskn "      # <-- 16-char App Password

def send_admin_email(subject: str, body: str) -> bool:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ADMIN_EMAIL
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        st.info(f"Note: email notification could not be sent ({e}).")
        return False

# ---------- Page setup ----------
st.set_page_config(page_title="NGO Sign Up | DoHub", layout="centered")

# ---------- Styles ----------
st.markdown("""
<style>
body { background-size: cover; background-repeat: no-repeat; background-attachment: fixed; }
.glass-card {
  background: rgba(0,0,0,0.4);
  box-shadow: 0 8px 32px 0 rgba(31,38,135,0.37);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2.5rem; width:100%; max-width:500px;
  margin: 3rem auto; border: 1px solid rgba(255,255,255,0.18);
}
h2, label, input, div, span, p, textarea { color: white !important; }
</style>
""", unsafe_allow_html=True)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ---------- UI ----------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>Welcome to DoHub</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Sign up as an NGO to get started.</p>", unsafe_allow_html=True)

st.session_state.setdefault("ngo_registered", False)
st.session_state.setdefault("ngo_registered_email", "")

with st.form("ngo_signup_form"):
    ngo_name = st.text_input("NGO Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    address = st.text_area("Address")
    phone = st.text_input("Phone Number")
    reg_id = st.text_input("Registration ID")
    logo = st.file_uploader("Upload Logo / Registration Document", type=["png", "jpg", "pdf"])

    submitted = st.form_submit_button("Register NGO")

    if submitted:
        # --- validations ---
        errs = []
        if not ngo_name: errs.append("NGO Name is required.")
        if not email: errs.append("Email is required.")
        elif not EMAIL_RE.match(email): errs.append("Please enter a valid email address.")
        if not password: errs.append("Password is required.")
        elif len(password) < 6: errs.append("Password must be at least 6 characters.")
        if not phone: errs.append("Phone Number is required.")  # ✅ compulsory
        if not reg_id: errs.append("Registration ID is required.")  # ✅ compulsory

        if errs:
            for e in errs:
                st.error(e)
        else:
            # 1. Register NGO as an auth user
            ok = register_user(email, password)
            if ok:
                # 2. Insert NGO details into 'ngos' table
                try:
                    supabase.table("ngos").insert({
                        "ngo_name": ngo_name,
                        "email": email,
                        "phone": phone,
                        "address": address,
                        "registration_id": reg_id
                    }).execute()
                except Exception as e:
                    st.warning(f"NGO metadata insert failed: {e}")

                st.success("✅ NGO registered successfully! Please check your email to verify before logging in.")
                st.session_state["ngo_registered"] = True
                st.session_state["ngo_registered_email"] = email

                # Email admin
                body = (
                    "A new NGO registered on DoHub:\n\n"
                    f"Name: {ngo_name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"Registration ID: {reg_id}\n"
                    f"Address: {address or '-'}\n"
                )
                send_admin_email("New NGO Registration", body)
            else:
                st.error("❌ This email could not be registered. It may already exist.")

# ---------- Post-success actions ----------
if st.session_state["ngo_registered"]:
    colA, colB = st.columns(2)
    with colA:
        if st.button("Go to Home"):
            st.switch_page("home.py")
    with colB:
        if st.button("Log In Now"):
            st.switch_page("home.py")

st.markdown(
    '<p style="text-align:center;">Already have an account? '
    '<a href="/home" style="color:white; text-decoration: underline;">Log in instead</a></p>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

