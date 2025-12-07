import os
import subprocess

# Redirect to the real app file
subprocess.run(["streamlit", "run", "src/app.py"])

