# DevTutor AI - Intelligent Programming Assistant Chatbot

> A multi-mode, full-stack programming tutor powered by **FastAPI** and the **Google Gemini API** (`gemini-2.5-flash`), featuring specialized prompts for **Code Debugging**, **Interactive Tutorials**, and **Technical Q&A**.

---

## 📌 Architecture Overview

```
 Student (Browser)
       ↕ (HTTP / JSON)
 FastAPI Application (app/main.py)
   ├── Static Files (HTML / CSS / JS with marked.js + highlight.js)
   ├── Mode Prompts (app/prompts.py: Debug | Tutorial | Q&A)
   └── Gemini Client (app/gemini_client.py: google-genai SDK)
       ↕ (SSL / API Key)
 Google Gemini API (gemini-2.5-flash)
```

---

## 🚀 Key Features

| Mode | Input | Formatted Output |
|---|---|---|
| **Debug Mode** 🐞 | Code + Language (+ optional error message) | 1. Errors with line numbers<br>2. Plain-language root cause<br>3. Corrected & formatted code<br>4. Prevention tip |
| **Tutorial Mode** 📚 | Concept/Topic + Language | 1. Concept definition & analogy<br>2. Syntax template<br>3. Annotated code example<br>4. Common pitfalls<br>5. Practice challenge |
| **Q&A Mode** 💡 | Technical question + Language context | Concise answer with practical code snippet |

### ✨ Standout Features
- **Modern Responsive UI**: Dark & Light mode toggle, high-contrast monospace code styling.
- **Copy Code Buttons**: Instant one-click copy on every code block with visual feedback.
- **Explain Line-by-Line**: Optional detailed execution flow breakdown.
- **Learner Level Customization**: Beginner, Intermediate, and Advanced difficulty options.
- **Guardrails**: Refuses non-programming questions to stay strictly focused on computer science.
- **Error Handling**: Friendly alerts for rate limits (429), invalid API keys, and missing configurations.
- **Interactive API Documentation**: Built-in Swagger UI at `/docs` and ReDoc at `/redoc`.

---

## 📁 Project Structure

```
ai-code-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, CORS, static routes, and endpoints
│   ├── gemini_client.py # Google GenAI SDK client, history handling & error recovery
│   ├── prompts.py       # Prompt engineering templates for Debug, Tutorial & QA
│   └── schemas.py       # Pydantic models for request validation & documentation
├── static/
│   ├── index.html       # Web chat interface
│   ├── style.css        # Responsive stylesheet with dark/light themes
│   └── script.js        # Markdown parsing, syntax highlighting & API calls
├── tests/
│   └── test_samples.md  # 20+ comprehensive test scenarios & verification table
├── .env.example         # Environment template for Gemini API key
├── .gitignore           # Git ignore rules for venv and secrets
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation and Viva guide
```

---

## 🛠️ Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher installed on your system.
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone / Open Directory & Create Virtual Environment
```bash
# In your terminal or command prompt:
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
Copy `.env.example` to `.env` and insert your Gemini API key:
```bash
copy .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-2.5-flash
HOST=127.0.0.1
PORT=8000
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```
or:
```bash
python -m app.main
```

### 6. Open the Application
- **Web Chat UI**: Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **FastAPI Interactive Docs (Swagger)**: Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web chat frontend (`index.html`) |
| `GET` | `/health` | Server status and Gemini configuration check |
| `POST` | `/debug` | Debug endpoint (takes code, language, error msg) |
| `POST` | `/tutorial` | Tutorial endpoint (takes topic, language) |
| `POST` | `/ask` | Q&A endpoint (takes question, language) |
| `POST` | `/chat` | Unified endpoint used by the chat interface |

---

## 🎓 Viva & Exam Preparation Guide

### Top Viva Questions & Model Answers

1. **Why did you choose Gemini Flash (`gemini-2.5-flash`) over other models?**
   > *Answer:* Gemini 2.5 Flash provides fast response times, high code generation quality, and a generous free-tier quota in Google AI Studio, making it ideal for interactive student tutoring without significant latency.

2. **What is a System Prompt and why does each mode have its own?**
   > *Answer:* A system prompt instructs the Large Language Model on its persona, output formatting constraints, and strict boundaries. By decoupling the system prompts into `prompts.py`, each mode (Debug, Tutorial, Q&A) enforces a predictable pedagogical structure without requiring the student to format their inputs.

3. **How do you prevent students from using the bot for non-programming queries?**
   > *Answer:* Guardrail rules embedded directly within all system prompts instruct the model to politely refuse questions unrelated to programming and software engineering.

4. **How are API rate limits and connection errors handled?**
   > *Answer:* The `gemini_client.py` module wraps API calls in robust try-except handlers. When a `429 RESOURCE_EXHAUSTED` or authentication error occurs, it catches the exception and returns a clear, actionable message to the student instead of crashing the server.

