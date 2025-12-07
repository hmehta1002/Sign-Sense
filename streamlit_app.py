import sys
import os

# Add the src folder to the system path so Python can find app.py
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Import and run the actual Streamlit app
import app
