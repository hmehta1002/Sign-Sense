import sys
import os

# Allow Python to find the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import app  # this runs src/app.py
