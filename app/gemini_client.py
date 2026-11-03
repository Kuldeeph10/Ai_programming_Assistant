"""
Gemini API Client integration using the official google-genai SDK.
Handles authentication, model invocation, chat history, and error recovery.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Global client cache
_client = None


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
    Supports multi-turn history.
    """
    client = get_gemini_client()
    model = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    from google.genai import types

    # Prepare system instruction
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,  # lower temperature for reliable, precise code generation
    )

    try:
        if history and len(history) > 0:
            # Build multi-turn contents list
            contents = []
            for msg in history:
                role = "user" if msg.get("role") == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))]
                    )
                )
            # Add the current user query
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_text)]
                )
            )

            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        else:
            response = client.models.generate_content(
                model=model,
                contents=user_text,
                config=config,
            )

        if not response.text:
            return "⚠️ The model returned an empty response. Please check your prompt or safety constraints."

        return response.text

    except Exception as exc:
        err_msg = str(exc)
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            return (
                "⚠️ **API Rate Limit Exceeded (429)**\n\n"
                "You have hit the Gemini API quota limit. Please wait 30-60 seconds before trying again, "
                "or switch to another Gemini API key in your `.env` file."
            )
        elif "API_KEY_INVALID" in err_msg or "400" in err_msg and "API key" in err_msg:
            return (
                "❌ **Invalid API Key**\n\n"
                "Your Google Gemini API key seems invalid. Please check the `GEMINI_API_KEY` in your `.env` file."
            )
        else:
            return f"❌ **Gemini API Error**: {err_msg}"

