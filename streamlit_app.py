import sys
import streamlit as st

# Ensure Python knows where to find the src folder
sys.path.append("src")

import app  # Imports src/app.py

app.main()
