import sys
from pathlib import Path
import streamlit as st

# --- Ensure src/ is in Python path ---
ROOT_DIR = Path(__file__).resolve().parent / "src"
sys.path.append(str(ROOT_DIR))

# --- Import main app router ---
import app  # this now points to src/app.py

if __name__ == "__main__":
    app.main()
