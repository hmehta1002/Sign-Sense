import streamlit as st

st.set_page_config(page_title="SignSense", layout="centered")

# Welcome Screen
st.title("SignSense")
st.write("Adaptive Quiz Platform for Inclusive Learning.")

if "page" not in st.session_state:
    st.session_state.page = "home"

# Navigation Logic
if st.session_state.page == "home":
    if st.button("Begin"):
        st.session_state.page = "mode_selection"

elif st.session_state.page == "mode_selection":
    st.subheader("Select Learning Mode")
    st.session_state.mode = st.radio(
        "Choose one:",
        ["Standard", "ADHD-Friendly", "Dyslexia-Friendly", "Autism-Friendly"]
    )
    if st.button("Continue"):
        st.session_state.page = "subject_selection"

elif st.session_state.page == "subject_selection":
    st.subheader("Choose Subject")
    st.session_state.subject = st.radio("Select:", ["Math", "English"])
    if st.button("Start Quiz"):
        st.session_state.page = "coming_soon"

elif st.session_state.page == "coming_soon":
    st.success("Quiz loading… (Feature under development)")
    if st.button("Return Home"):
        st.session_state.page = "home"

