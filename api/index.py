"""Vercel entrypoint.

Vercel's Python runtime auto-detects any `.py` file inside `api/` and, when it
exposes an ASGI callable named `app`, serves it as a Serverless Function.

The application code lives under `src/` (src layout) and is not pip-installed on
Vercel (requirements.txt has no editable install), so `src/` is added to the
import path explicitly before importing the FastAPI app.
"""

import os
import sys

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from apils.main import app  # noqa: E402

__all__ = ["app"]
