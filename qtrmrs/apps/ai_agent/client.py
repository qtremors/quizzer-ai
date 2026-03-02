import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level cached client instance
_client = None
_cached_api_key = None


def get_gemini_client():
    """
    Get or create a cached Gemini client instance.
    
    SEC-018: The client is invalidated and re-created if the API key
    changes (e.g., key rotation), rather than requiring a process restart.
    """
    global _client, _cached_api_key

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured - AI features will not work")
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    # Invalidate cache if key changed
    if _client is not None and _cached_api_key == api_key:
        return _client

    _client = genai.Client(api_key=api_key)
    _cached_api_key = api_key
    return _client
