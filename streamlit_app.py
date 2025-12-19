import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent / "src"
sys.path.append(str(BASE))

import app
import importlib
importlib.reload(app)

if __name__ == "__main__":
    app.main()
