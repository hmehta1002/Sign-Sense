import sys
import os
import streamlit as st

# Allow Python to find the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

st.set_page_config(page_title="SignSense")

try:
    import app  # Run the actual app
except Exception as e:
    st.error("⚠️ Something went wrong.")
    st.code(str(e))
    raise
