# src/tests/conftest.py
# Ensure project root is on sys.path so tests can import the `src` package.
import sys
from pathlib import Path

# repo root is two levels up from src/tests/
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
