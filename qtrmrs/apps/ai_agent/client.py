import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

def get_gemini_client():
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured - AI features will not work")
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")
    
    return genai.Client(api_key=api_key)
