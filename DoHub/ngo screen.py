import streamlit as st

# Page settings
st.set_page_config(layout="centered", page_title="DoHub - NGO Sign Up")

# Light/Dark mode toggle
mode = st.sidebar.selectbox("Theme", ["Dark", "Light"])

# Color config
if mode == "Dark":
    bg = "#121212"
    text = "#ffffff"
    input_bg = "#1e1e1e"
    border = "#333333"
    placeholder = "#aaaaaa"
    button_bg = "#2c2c2c"
    button_hover = "#3c3c3c"
else:
    bg = "#f5f5f5"
    text = "#111111"
    input_bg = "#ffffff"
    border = "#dddddd"
    placeholder = "#666666"
    button_bg = "#ffffff"
    button_hover = "#eeeeee"

# Inject working CSS
st.markdown(f"""
    <style>
    html, body, .stApp {{
        background-color: {bg} !important;
        color: {text} !important;
        font-family: 'Poppins', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, label, p, span, div {{
        color: {text} !important;
    }}
    input, textarea {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem;
    }}
    input::placeholder, textarea::placeholder {{
        color: {placeholder} !important;
    }}
    .stButton > button {{
        background-color: {button_bg} !important;
        color: {text} !important;
        border: 1px solid {border};
        border-radius: 14px !important;
        padding: 12px 28px !important;
        font-weight: 600;
        transition: 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: {button_hover} !important;
        transform: scale(1.03);
    }}
    .stFileUploader label, .stFileUploader span {{
        color: {text} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown(f"<h2 style='text-align: center;'>Welcome to DoHub</h2>", unsafe_allow_html=True)

# Form Container
with st.container():
    st.markdown("<div style='background: rgba(255, 255, 255, 0.05); padding: 3rem; border-radius: 20px; max-width: 450px; margin: 0 auto;'>", unsafe_allow_html=True)

    st.text_input("NGO Name", placeholder="E.g. Helping Hands")
    st.text_input("Email", placeholder="you@example.com")
    st.text_input("Password", type="password", placeholder="●●●●●●●●")
    st.text_input("Confirm Password", type="password", placeholder="●●●●●●●●")
    st.file_uploader("Upload Registration Document (PDF)")
    st.button("Sign Up")

    st.markdown("<p style='text-align: center; margin-top: 1rem;'>Already have an account? <a href='#' style='color:inherit; text-decoration:underline;'>Log in</a></p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
