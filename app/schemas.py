"""
Pydantic Request & Response Models for the AI Programming Assistant.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ModeEnum(str, Enum):
    DEBUG = "debug"
    TUTORIAL = "tutorial"
    QA = "qa"


class DifficultyEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message author: 'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")


class DebugRequest(BaseModel):
    code: str = Field(..., description="Source code containing bugs or needing review", min_length=1)
    language: str = Field(default="python", description="Programming language (e.g., Python, C++, JavaScript)")
    error_message: Optional[str] = Field(default=None, description="Optional compiler or runtime error message")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.BEGINNER, description="Target learner level")
    explain_line_by_line: bool = Field(default=False, description="Whether to include line-by-line explanation")


class TutorialRequest(BaseModel):
    topic: str = Field(..., description="Concept or topic name, e.g. 'Recursion', 'Pointers in C++'", min_length=2)
    language: str = Field(default="python", description="Programming language context")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.BEGINNER, description="Target learner level")


class QARequest(BaseModel):
    question: str = Field(..., description="Programming-related question", min_length=2)
    language: Optional[str] = Field(default=None, description="Optional programming language context")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.BEGINNER, description="Target learner level")


class UnifiedChatRequest(BaseModel):
    mode: ModeEnum = Field(default=ModeEnum.QA, description="Active assistant mode")
    message: str = Field(..., description="User prompt or code text", min_length=1)
    language: str = Field(default="python", description="Selected programming language")
    error_message: Optional[str] = Field(default=None, description="Optional runtime/compiler error text")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.BEGINNER, description="Target learner level")
    explain_line_by_line: bool = Field(default=False, description="Include line-by-line breakdown")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous conversation turns")


class BotResponse(BaseModel):
    status: str = Field(default="success", description="Status code ('success' or 'error')")
    mode: ModeEnum = Field(..., description="Mode that handled the request")
    response_text: str = Field(..., description="Formatted markdown response from Gemini")


class HealthResponse(BaseModel):
    status: str
    model: str
    gemini_configured: bool

