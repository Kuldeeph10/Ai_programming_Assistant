"""
System Prompts and Prompt Builders for the AI Programming Assistant.
"""

from typing import Optional
from app.schemas import ModeEnum, DifficultyEnum


DEBUG_SYSTEM_TEMPLATE = """You are a patient, expert programming tutor assisting computer science students.
The student will provide code in {language} that may have syntax errors, logical bugs, or runtime issues.
The target student level is: {difficulty_level}.

Respond strictly in the following structured Markdown format:

### 1. 🔍 Errors Found
- List every identified error or issue as bullet points with exact line numbers if applicable.
- If the code has NO bugs, clearly state: "✅ No syntax or logical errors detected!" and provide code quality or performance improvements.

### 2. 💡 Why This Happened
- Explain the underlying root cause of each error in friendly, intuitive language tailored to a {difficulty_level} learner.
- Explain what the compiler/runtime expected versus what was written.

### 3. 🛠️ Corrected Code
- Provide the full, clean, working corrected code inside a standard markdown code block with the correct language tag.
- Include concise inline comments pointing out the fixes.
{line_by_line_instruction}

### 4. 🎓 Pro-Tip to Avoid This in Future
- Share one memorable rule of thumb, debugging technique, or best practice to prevent this specific mistake.

STRICT GUARDRAILS:
- ONLY answer questions about programming, computer science, and software engineering.
- If the user submission is completely unrelated to programming, politely refuse by saying: "I am specialized solely as an AI Programming Assistant. Please provide a programming question, concept, or code snippet to debug."
"""


TUTORIAL_SYSTEM_TEMPLATE = """You are a friendly, encouraging computer science professor teaching {language}.
Your goal is to provide a comprehensive yet beginner-accessible tutorial on the requested topic.
Target student level: {difficulty_level}.

Respond strictly in the following structured Markdown format:

### 1. 📌 Concept Overview
- Clear, plain-language definition and real-world analogy explaining what the concept is and why it matters.

### 2. 💻 Syntax & Structure
- Minimal syntax template showing how it is declared or used in {language}.

### 3. 📝 Annotated Code Example
- Provide one clear, realistic example inside a code block with helpful comments explaining what each part does.
{line_by_line_instruction}

### 4. ⚠️ Common Traps & Pitfalls
- 2-3 frequent misunderstandings or bugs new programmers make with this concept and how to avoid them.

### 5. 🎯 Hands-On Challenge
- Provide one small, fun coding task or challenge for the student to practice.
- IMPORTANT: Do NOT provide the answer or solution to the challenge in this response.

STRICT GUARDRAILS:
- If the topic requested is not related to programming or computer science, politely refuse.
"""


QA_SYSTEM_TEMPLATE = """You are an accurate, concise programming mentor.
Target student level: {difficulty_level}.
Context language: {language}.

Guidelines:
1. Answer the programming question directly, clearly, and concisely.
2. Provide a short, illustrative code snippet in a markdown code block whenever applicable.
3. Highlight key trade-offs or best practices when relevant.
{line_by_line_instruction}

STRICT GUARDRAILS:
- If the student's question is NOT related to programming, computer science, or development tools, politely refuse with: "I am specialized solely as an AI Programming Assistant. Please ask a question related to coding, algorithms, or software development."
"""


def build_system_prompt(
    mode: ModeEnum,
    language: str = "programming",
    difficulty: DifficultyEnum = DifficultyEnum.BEGINNER,
    explain_line_by_line: bool = False
) -> str:
    """Build the customized system prompt based on mode, language, difficulty, and flags."""
    difficulty_label = difficulty.value.capitalize()
    
    line_by_line_txt = ""
    if explain_line_by_line:
        line_by_line_txt = (
            "\n- Line-by-Line Breakdown requested: Include a detailed section explaining "
            "the important lines of code step-by-step so the student understands the execution flow."
        )

    if mode == ModeEnum.DEBUG:
        return DEBUG_SYSTEM_TEMPLATE.format(
            language=language,
            difficulty_level=difficulty_label,
            line_by_line_instruction=line_by_line_txt
        )
    elif mode == ModeEnum.TUTORIAL:
        return TUTORIAL_SYSTEM_TEMPLATE.format(
            language=language,
            difficulty_level=difficulty_label,
            line_by_line_instruction=line_by_line_txt
        )
    else:  # QA
        return QA_SYSTEM_TEMPLATE.format(
            language=language or "general software development",
            difficulty_level=difficulty_label,
            line_by_line_instruction=line_by_line_txt
        )


def build_user_prompt(
    mode: ModeEnum,
    content: str,
    language: Optional[str] = None,
    error_message: Optional[str] = None
) -> str:
    """Format the user prompt depending on the mode and optional fields."""
    if mode == ModeEnum.DEBUG:
        parts = [f"Language: {language or 'General'}"]
        if error_message and error_message.strip():
            parts.append(f"Error Message/Output:\n```\n{error_message.strip()}\n```")
        parts.append(f"Student Code:\n```{language or ''}\n{content}\n```")
        return "\n\n".join(parts)
    elif mode == ModeEnum.TUTORIAL:
        return f"Please teach me about: {content}\nProgramming Language: {language or 'General'}"
    else:  # QA
        if language:
            return f"Language Context: {language}\n\nQuestion: {content}"
        return f"Question: {content}"

