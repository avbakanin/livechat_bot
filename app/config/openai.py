"""
OpenAI API configuration settings.
"""
import os
from typing import Optional, TypedDict

from dotenv import load_dotenv

load_dotenv()


class OpenAIConfig(TypedDict):
    """OpenAI configuration type."""

    api_key: Optional[str]
    model: str
    temperature: float
    max_tokens: int
    base_url: Optional[str]
    FREE_MESSAGE_LIMIT: int


OPENAI_CONFIG: OpenAIConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1000,
    "base_url": None,  # Use default OpenAI API URL
    "FREE_MESSAGE_LIMIT": 50,
}
