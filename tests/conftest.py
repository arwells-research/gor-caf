from __future__ import annotations

# Ensure `import gor_caf` works when running tests without an editable install.
# This is intentionally lightweight and does not change runtime behavior for
# installed packages.

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
