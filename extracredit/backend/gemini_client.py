from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def _read_api_key() -> Optional[str]:
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GENERATIVEAI_API_KEY")
    )


def get_gemini_api_key() -> Optional[str]:
    # Load from backend/.env regardless of current working directory,
    # while still allowing environment variables to override.
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)
    load_dotenv(override=False)
    return _read_api_key()


def is_gemini_configured() -> bool:
    return bool(get_gemini_api_key())


def build_gemini_model(model_name: str):
    """Create a google.generativeai GenerativeModel if an API key is configured."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key not configured. Set GEMINI_API_KEY (or GOOGLE_API_KEY) in backend/.env"
        )

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)
