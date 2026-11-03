"""
FastAPI Server & Route Handlers for the AI Programming Assistant Chatbot.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import (
    ModeEnum,
    DebugRequest,
    TutorialRequest,
    QARequest,
    UnifiedChatRequest,
    BotResponse,
    HealthResponse,
)
from app.prompts import build_system_prompt, build_user_prompt
from app.gemini_client import ask_gemini, DEFAULT_MODEL

# Determine base paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="AI Programming Assistant Chatbot API",
    description="A multi-mode programming tutor powered by Google Gemini and FastAPI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for front-end clients or local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", summary="Serve the Web Chat Interface", include_in_schema=False)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "AI Programming Assistant API is running. Visit /docs for the Swagger UI."
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Returns the operational status of the service and Gemini configuration."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    configured = bool(api_key and api_key != "your_gemini_api_key_here")
    return HealthResponse(
        status="healthy",
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        gemini_configured=configured,
    )


@app.post("/debug", response_model=BotResponse, tags=["Modes"])
async def debug_code_endpoint(payload: DebugRequest):
    """
    Debug mode endpoint:
    Accepts student code, language, and optional error message.
    Returns error list, root cause explanation, corrected code, and best practice tips.
    """
    try:
        sys_prompt = build_system_prompt(
            mode=ModeEnum.DEBUG,
            language=payload.language,
            difficulty=payload.difficulty,
            explain_line_by_line=payload.explain_line_by_line,
        )
        user_prompt = build_user_prompt(
            mode=ModeEnum.DEBUG,
            content=payload.code,
            language=payload.language,
            error_message=payload.error_message,
        )
        answer = ask_gemini(system_prompt=sys_prompt, user_text=user_prompt)
        return BotResponse(mode=ModeEnum.DEBUG, response_text=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/tutorial", response_model=BotResponse, tags=["Modes"])
async def tutorial_endpoint(payload: TutorialRequest):
    """
    Tutorial mode endpoint:
    Accepts concept topic and language.
    Returns clear definition, syntax, commented example, common traps, and a practice challenge.
    """
    try:
        sys_prompt = build_system_prompt(
            mode=ModeEnum.TUTORIAL,
            language=payload.language,
            difficulty=payload.difficulty,
        )
        user_prompt = build_user_prompt(
            mode=ModeEnum.TUTORIAL,
            content=payload.topic,
            language=payload.language,
        )
        answer = ask_gemini(system_prompt=sys_prompt, user_text=user_prompt)
        return BotResponse(mode=ModeEnum.TUTORIAL, response_text=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ask", response_model=BotResponse, tags=["Modes"])
async def ask_endpoint(payload: QARequest):
    """
    Q&A mode endpoint:
    Accepts a student programming question.
    Returns concise technical explanation with brief illustrative code snippet.
    """
    try:
        sys_prompt = build_system_prompt(
            mode=ModeEnum.QA,
            language=payload.language or "General",
            difficulty=payload.difficulty,
        )
        user_prompt = build_user_prompt(
            mode=ModeEnum.QA,
            content=payload.question,
            language=payload.language,
        )
        answer = ask_gemini(system_prompt=sys_prompt, user_text=user_prompt)
        return BotResponse(mode=ModeEnum.QA, response_text=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/chat", response_model=BotResponse, tags=["Unified Chat"])
async def unified_chat_endpoint(payload: UnifiedChatRequest):
    """
    Unified chat endpoint used by the interactive frontend.
    Handles mode switching, difficulty level, multi-turn conversation history,
    optional error messages, and line-by-line explanation.
    """
    try:
        sys_prompt = build_system_prompt(
            mode=payload.mode,
            language=payload.language,
            difficulty=payload.difficulty,
            explain_line_by_line=payload.explain_line_by_line,
        )
        user_prompt = build_user_prompt(
            mode=payload.mode,
            content=payload.message,
            language=payload.language,
            error_message=payload.error_message,
        )

        history_dicts = [msg.model_dump() for msg in payload.history]

        answer = ask_gemini(
            system_prompt=sys_prompt,
            user_text=user_prompt,
            history=history_dicts,
        )
        return BotResponse(mode=payload.mode, response_text=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting AI Programming Assistant on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

