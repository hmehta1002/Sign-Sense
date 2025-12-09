import sys
from pathlib import Path

# Ensure Streamlit can find src/
BASE_DIR = Path(__file__).resolve().parent / "src"
sys.path.append(str(BASE_DIR))

# Import your main app file
import app

if __name__ == "__main__":
    app.main()
