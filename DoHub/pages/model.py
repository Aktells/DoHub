# model.py
import streamlit as st
import pandas as pd
from bot import get_bot_response, filter_candidates
import sys, importlib
if not st.session_state.get("auth", False):
    st.warning("Please log in first.")
    st.switch_page("home.py")   # send them back

st.set_page_config(page_title="NGO Recommender", layout="wide")
st.title("Find the right NGO for your donation or volunteering")
# Force readable text inside selected multiselect "pills" in dark mode
st.markdown("""
<style>
/* Selected tag pill container */
.stMultiSelect [data-baseweb="tag"]{
  background-color:#ffffff !important;   /* keep pill white */
  color:#111111 !important;               /* make text dark */
  border:1px solid #444 !important;
}
/* Text and close “x” inside the pill */
.stMultiSelect [data-baseweb="tag"] *{
  color:#111111 !important;
  fill:#111111 !important;
}
/* Also fix the little 'x' hover */
.stMultiSelect [data-baseweb="tag"] svg{
  color:#111111 !important;
  fill:#111111 !important;
}
</style>
""", unsafe_allow_html=True)


# Sidebar: city input
with st.sidebar:
    st.header("Your Location")
    city = st.text_input("City", value="Jaipur")

# 🔑 New: Free text query
st.subheader("Quick ask (optional)")
free_query = st.text_area("Type in plain text what you want to donate or where you want to help:")

st.subheader("Or fill the structured form")
col1, col2 = st.columns(2)

with col1:
    needs = st.multiselect(
        "Causes you care about",
        [
            "Health", "Education", "Environment", "Animal Welfare", "Women Empowerment",
            "Child Protection", "Hunger Relief", "Elderly Care", "Disability Inclusion",
            "Disaster Relief", "WASH", "Livelihoods", "Arts & Culture", "Youth", "Sports"
        ],
        default=["Education", "Hunger Relief"]
    )
    items = st.multiselect(
        "Items to donate",
        [
            "notebooks", "stationery", "school bags", "tablets", "dry rations", "grains",
            "canned food", "saplings", "blankets", "wheelchairs", "sanitary pads",
            "pet food", "medical supplies", "craft tools", "cricket kits"
        ],
    )

with col2:
    skills = st.multiselect(
        "Skills you can volunteer",
        [
            "teaching", "mentoring", "curriculum design", "logistics", "community outreach",
            "animal handling", "veterinary assistance", "health camp organization",
            "business mentoring", "fundraising", "digital marketing", "water testing",
            "coaching", "event management"
        ],
    )
    notes = st.text_area("Anything else we should know? (optional)")

if st.button("Find NGOs"):
    # 🔑 If free text given, let that override structured form
    if free_query.strip():
        profile = {
            "city": city,
            "needs": [],
            "items_to_donate": [],
            "skills": [],
            "notes": free_query.strip()
        }
    else:
        profile = {
            "city": city,
            "needs": needs,
            "items_to_donate": items,
            "skills": skills,
            "notes": notes
        }

    with st.spinner("Matching you with NGOs..."):
        result_text = get_bot_response(profile)

    st.subheader("Recommended NGOs")
    st.write(result_text)

    # If we fell back to heuristics, show top candidates table
    if "heuristic" in result_text.lower():
        cands = filter_candidates(profile, top_k=5)
        st.dataframe(
            cands[[
                "name", "city", "categories",
                "accepts_items", "accepts_volunteer_skills", "description"
            ]]
        )

st.divider()
st.caption(
    "Tip: try to use the form"
)


