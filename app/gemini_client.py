"""
Gemini API Client integration using the official google-genai SDK.
Handles authentication, model invocation, multi-model fallback, chat history, and error recovery.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

# Fallback sequence in case a model is deprecated (404) or experiencing high demand (503)
CANDIDATE_MODELS = [
    DEFAULT_MODEL,
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
]

# Global client and working model cache
_client = None
_active_model = None


def get_gemini_client():
    """Lazily initialize and return the Google GenAI client."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not configured! Please open the `.env` file, "
            "add your Google AI Studio API key, and restart the server."
        )

    try:
        from google import genai
        _client = genai.Client(api_key=api_key)
        return _client
    except ImportError as e:
        raise RuntimeError(
            "The `google-genai` package is not installed. "
            "Please run: pip install -r requirements.txt"
        ) from e


def ask_gemini(
    system_prompt: str,
    user_text: str,
    history: Optional[List[dict]] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Call Gemini with a dedicated system instruction and user prompt.
    Supports multi-turn history and automatic resilient fallback if a model is unavailable.
    """
    global _active_model
    client = get_gemini_client()
    from google.genai import types

    # Prepare system instruction
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,
    )

    # Determine models to try (prioritize explicit model or currently working cached model)
    target_models = []
    if model_name:
        target_models.append(model_name)
    elif _active_model:
        target_models.append(_active_model)

    for m in CANDIDATE_MODELS:
        if m and m not in target_models:
            target_models.append(m)

    # Format contents
    if history and len(history) > 0:
        contents = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.get("content", ""))]
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)]
            )
        )
    else:
        contents = user_text

    last_error = None

    for candidate in target_models:
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=contents,
                config=config,
            )

            if not response.text:
                return "⚠️ The model returned an empty response. Please check your prompt or safety constraints."

            _active_model = candidate
            return response.text

        except Exception as exc:
            err_msg = str(exc)
            last_error = err_msg

            # If 404 (model deprecated/not available) or 503 (high demand spike), try next candidate
            if "404" in err_msg or "NOT_FOUND" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg:
                continue

            # If rate limit or invalid API key, return immediate user-friendly feedback
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                return (
                    "⚠️ **API Rate Limit Exceeded (429)**\n\n"
                    "You have hit the Gemini API quota limit. Please wait 30-60 seconds before trying again, "
                    "or switch to another Gemini API key in your `.env` file."
                )
            elif "API_KEY_INVALID" in err_msg or ("400" in err_msg and "API key" in err_msg):
                return (
                    "❌ **Invalid API Key**\n\n"
                    "Your Google Gemini API key seems invalid. Please check the `GEMINI_API_KEY` in your `.env` file."
                )
            else:
                return f"❌ **Gemini API Error**: {err_msg}"

    return f"❌ **Gemini API Error**: All model attempts failed. Last error: {last_error}"
