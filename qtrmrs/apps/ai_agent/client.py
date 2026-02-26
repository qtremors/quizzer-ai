import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cached client instance
_client = None


def get_gemini_client():
    """Get or create a cached Gemini client instance."""
    global _client
    if _client is not None:
        return _client

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured - AI features will not work")
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    
    _client = genai.Client(api_key=api_key)
    return _client
