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

# OpenAI client instance
openai_client = None

def initialize_openai_client():
    """Initialize OpenAI client."""
    global openai_client
    
    try:
        from openai import OpenAI
        
        if OPENAI_CONFIG["api_key"]:
            openai_client = OpenAI(
                api_key=OPENAI_CONFIG["api_key"],
                base_url=OPENAI_CONFIG["base_url"]
            )
            print("✅ OpenAI client initialized successfully")
        else:
            print("⚠️ OpenAI API key not found, client not initialized")
            openai_client = None
    except ImportError:
        print("❌ OpenAI library not installed")
        openai_client = None
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        openai_client = None

# Initialize client on import
initialize_openai_client()