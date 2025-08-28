import streamlit as st

# Protect page
if not st.session_state.get("auth", False):
    st.warning("Please log in first.")
    st.switch_page("home.py")

st.title("👤 Profile")

st.write("Welcome to your profile page.")
st.write(f"**Email:** {st.session_state.get('user_email', 'N/A')}")

if st.button("Log Out"):
    st.session_state.clear()
    st.switch_page("home.py")
