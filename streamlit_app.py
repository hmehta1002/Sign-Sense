import os
import sys
import streamlit as st

# Get absolute path to project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add src folder to Python path
SRC_PATH = os.path.join(ROOT_DIR, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Now safely import the app
try:
    import app
    app.main()
except Exception as e:
    st.error(f"⚠️ Import failed: {e}")
    st.write("Check if file name is exactly `src/app.py`")
