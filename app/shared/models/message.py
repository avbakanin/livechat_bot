"""
Message domain models.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Message:
    """Message model."""
    id: Optional[int]
    user_id: int
    role: str
    text: str
    created_at: Optional[datetime] = None


@dataclass
class MessageCreate:
    """Message creation data."""
    user_id: int
    role: str
    text: str


@dataclass
class MessageContext:
    """Message context for OpenAI API."""
    role: str
    text: str


@dataclass
class OpenAIMessage:
    """OpenAI API message format."""
    role: str
    content: str


@dataclass
class ChatHistory:
    """Chat history data."""
    messages: List[MessageContext]
    system_prompt: str
