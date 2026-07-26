"""
Application configuration and settings.

Centralizes all constants, environment variable loading,
and LLM initialization used throughout the application.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# ─── Load Environment Variables ───
load_dotenv()

# ─── Application Settings ───
APP_TITLE: str = "Langchain: Chat with SQL Database"

# ─── Database Identifiers ───
LOCALDB: str = "USE_LOCALDB"
MYSQLDB: str = "USE_MYSQLDB"

# ─── Model Configuration ───
MODEL_NAME: str = "llama-3.3-70b-versatile"


def get_llm(api_key: str, model_name: str = MODEL_NAME) -> ChatGroq:
    """Create and return a configured ChatGroq LLM instance.

    Args:
        api_key: The Groq API key for authentication.
        model_name: Model identifier string (defaults to MODEL_NAME).

    Returns:
        A ChatGroq instance configured for tool execution.
    """
    # Disable streaming for experimental models that reject tool_choice during stream
    use_streaming = not model_name.startswith("openai/")

    return ChatGroq(
        model=model_name,
        streaming=use_streaming,
        api_key=api_key,
    )
