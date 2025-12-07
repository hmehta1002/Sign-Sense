import sys
import os
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

st.set_page_config(page_title="SignSense")

st.write("Loading app...")

try:
    import app
    st.success("App loaded successfully! 🎉")
except Exception as e:
    st.error("❌ The app failed to start. Here is the real error:")
    st.exception(e)
