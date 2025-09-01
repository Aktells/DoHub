import streamlit as st
from db import supabase

st.set_page_config(page_title="DoHub | Verify Email", layout="centered")

# -------------------
# HIDE FROM SIDEBAR
# -------------------
st.markdown("""
<style>
/* Hide Verify page from sidebar navigation */
section[data-testid="stSidebar"] li a span:has-text("Verify") {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------
# STYLES
# -------------------
st.markdown("""
<style>
html, body, .stApp { background: #0f1115; }

.glass-card {
  background: rgba(255,255,255,0.07);
  box-shadow: 0 8px 32px rgba(0,0,0,0.30);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2.5rem;
  width: 100%;
  max-width: 600px;
  margin: 10vh auto;
  border: 1px solid rgba(255,255,255,0.14);
  color: #fff;
  text-align: center;
}

.glass-title {
  font-size: 2.4rem;
  font-weight: 800;
  margin-bottom: 1rem;
}

.glass-sub {
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: #e7e7e7;
}
</style>
""", unsafe_allow_html=True)

# -------------------
# PAGE CONTENT
# -------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="glass-title">📧 Verify Your Email</div>', unsafe_allow_html=True)
st.markdown('<div class="glass-sub">We’re confirming your email address so you can start using DoHub.</div>', unsafe_allow_html=True)

# -------------------
# TOKEN HANDLING
# -------------------
params = st.experimental_get_query_params()
token = params.get("access_token", [None])[0]

if token:
    try:
        # Supabase Python SDK doesn’t expose a direct helper,
        # so we make a raw request to confirm signup token
        session = supabase.auth._client._request(
            "POST",
            f"{supabase.auth.api_url}/token?grant_type=signup",
            {"access_token": token}
        )

        if session and "access_token" in session:
            st.success("✅ Your email has been verified! You can now log in.")
            if st.button("Go to Login"):
                st.switch_page("home.py")
        else:
            st.error("❌ Verification failed. The link may be invalid or expired.")
    except Exception as e:
        st.error(f"Error verifying: {e}")
else:
    # If no token → accessed manually
    st.info("Please use the verification link sent to your email to open this page.")

    # Allow resend
    email = st.text_input("Didn’t get the link? Enter your email to resend:")
    if st.button("Resend Verification"):
        try:
            resp = supabase.auth.resend({"type": "signup", "email": email})
            if resp:
                st.success(f"✅ A new verification link has been sent to {email}.")
            else:
                st.error("❌ Could not resend verification email.")
        except Exception as e:
            st.error(f"Error resending email: {e}")

st.markdown('</div>', unsafe_allow_html=True)
