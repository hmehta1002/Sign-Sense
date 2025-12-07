import sys
import os

# Ensure src can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import app

# Run the real UI
app.main()
