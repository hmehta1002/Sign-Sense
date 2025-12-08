import os
import sys
import streamlit as st

# Make sure Python can see the src/ folder
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import app  # this is src/app.py

app.main()
