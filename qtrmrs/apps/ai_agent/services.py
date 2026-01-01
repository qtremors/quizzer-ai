import json
import logging
import time
from typing import Optional, Union
from django.conf import settings
from .client import get_gemini_client
from .prompts import (
    QUIZ_GENERATION_PROMPT, EXPLANATION_PROMPT, INTENT_PARSING_PROMPT,
    GENERAL_QUIZ_PROMPT, GENERAL_INTENT_PROMPT
)

logger = logging.getLogger(__name__)


class AIError:
    """Represents an AI generation error with details."""
    def __init__(self, error_type: str, message: str, suggestion: str = ""):
        self.error_type = error_type
        self.message = message
        self.suggestion = suggestion
    
    def __bool__(self):
        return False  # So it evaluates as falsy like empty list


class QuizGenerator:
    """
    Service class to handle AI interactions for Quizzes.
    Supports both programming and general-purpose quizzes.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.genai = get_gemini_client()
        self.model_name = model_name or getattr(settings, 'DEFAULT_AI_MODEL', 'gemini-flash-latest')
        self.model = self.genai.GenerativeModel(self.model_name)

    def _handle_error(self, e: Exception, operation: str) -> AIError:
        """Parse exception and return appropriate AIError."""
        error_str = str(e).lower()
        
        if '429' in str(e) or 'quota' in error_str or 'rate' in error_str:
            return AIError(
                error_type='quota',
                message=f"API quota exceeded for model: {self.model_name}",
                suggestion="Try selecting a different AI model, or wait a few minutes before trying again."
            )
        elif '404' in str(e) or 'not found' in error_str:
            return AIError(
                error_type='model_not_found',
                message=f"Model '{self.model_name}' not available",
                suggestion="This model may be deprecated. Try 'Gemini Flash (Latest)' instead."
            )
        elif '403' in str(e) or 'permission' in error_str or 'api key' in error_str:
            return AIError(
                error_type='auth',
                message="API authentication failed",
                suggestion="Please check your API key configuration."
            )
        elif 'timeout' in error_str or 'deadline' in error_str:
            return AIError(
                error_type='timeout',
                message="Request timed out",
                suggestion="The AI is taking too long. Try again or use a faster model."
            )
        else:
            logger.error(f"{operation} Error: {e}")
            return AIError(
                error_type='unknown',
                message="AI generation failed unexpectedly",
                suggestion="Try again or select a different AI model."
            )

    # ==========================================
    # PROGRAMMING QUIZ METHODS
    # ==========================================

    def generate_quiz(
        self, 
        language: str, 
        topic: str, 
        level: str, 
        num_questions: int = 5, 
        include_code: bool = False
    ) -> Union[list[dict], AIError]:
        """
        Generates a structured programming quiz using Gemini.
        Returns list of questions on success, AIError on failure.
        """
        if include_code:
            code_instruction = "Each question MUST include a relevant code snippet that the user must analyze to answer."
        else:
            code_instruction = "Questions should be conceptual. Do NOT include long code snippets."

        prompt = QUIZ_GENERATION_PROMPT.format(
            language=language,
            topic=topic,
            level=level,
            num_questions=num_questions,
            code_instruction=code_instruction
        )

        start_time = time.time()
        logger.info(f"Generating quiz: model={self.model_name}, language={language}, topic={topic}, level={level}, num_questions={num_questions}")
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            elapsed = time.time() - start_time
            quiz_data = json.loads(response.text)
            questions = quiz_data.get('questions', [])
            logger.info(f"Quiz generated successfully: {len(questions)} questions in {elapsed:.2f}s")
            return questions
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Quiz generation failed after {elapsed:.2f}s: {e}")
            return self._handle_error(e, "Quiz Generation")

    def parse_intent(self, user_message: str) -> dict:
        """
        Converts natural language into structured programming quiz parameters.
        """
        prompt = INTENT_PARSING_PROMPT.format(user_message=user_message)
        
        try:
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Intent Parsing Error: {e}")
            return {
                "language": "General",
                "topic": "Random",
                "level": "Intermediate",
                "count": 5
            }

    # ==========================================
    # GENERAL PURPOSE QUIZ METHODS
    # ==========================================

    def generate_general_quiz(
        self, 
        subject: str, 
        topic: str, 
        level: str, 
        num_questions: int = 5
    ) -> Union[list[dict], AIError]:
        """
        Generates a general-purpose quiz on any topic (non-programming).
        Returns list of questions on success, AIError on failure.
        """
        prompt = GENERAL_QUIZ_PROMPT.format(
            subject=subject,
            topic=topic,
            level=level,
            num_questions=num_questions
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            quiz_data = json.loads(response.text)
            return quiz_data.get('questions', [])
        except Exception as e:
            return self._handle_error(e, "General Quiz Generation")

    def parse_general_intent(self, user_message: str) -> dict:
        """
        Converts natural language into structured general quiz parameters.
        """
        prompt = GENERAL_INTENT_PROMPT.format(user_message=user_message)
        
        try:
            response = self.model.generate_content(
                prompt, 
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"General Intent Parsing Error: {e}")
            return {
                "subject": "General Knowledge",
                "topic": "Trivia",
                "level": "Intermediate",
                "count": 5
            }

    # ==========================================
    # SHARED METHODS
    # ==========================================

    def generate_explanation(
        self, 
        question_text: str, 
        user_answer: str, 
        correct_answer: str
    ) -> str:
        """
        Generates a concise explanation for why the user was wrong.
        Uses the EXPLANATION_PROMPT constant for consistency.
        """
        prompt = EXPLANATION_PROMPT.format(
            question_text=question_text,
            user_answer=user_answer,
            correct_answer=correct_answer
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Explanation Generation Error: {e}")
            if '429' in str(e) or 'quota' in str(e).lower():
                return f"⚠️ Could not generate explanation (API quota exceeded for {self.model_name}). Try a different model."
            return "Unable to generate explanation at this moment."

    # ==========================================
    # ASYNC METHODS (for ASGI/Django Channels)
    # ==========================================

    async def generate_quiz_async(
        self, 
        language: str, 
        topic: str, 
        level: str, 
        num_questions: int = 5, 
        include_code: bool = False
    ) -> Union[list[dict], AIError]:
        """Async version of generate_quiz for ASGI deployments."""
        import asyncio
        return await asyncio.to_thread(
            self.generate_quiz, language, topic, level, num_questions, include_code
        )

    async def generate_general_quiz_async(
        self, 
        subject: str, 
        topic: str, 
        level: str, 
        num_questions: int = 5
    ) -> Union[list[dict], AIError]:
        """Async version of generate_general_quiz for ASGI deployments."""
        import asyncio
        return await asyncio.to_thread(
            self.generate_general_quiz, subject, topic, level, num_questions
        )

    async def parse_intent_async(self, user_message: str) -> dict:
        """Async version of parse_intent for ASGI deployments."""
        import asyncio
        return await asyncio.to_thread(self.parse_intent, user_message)

    async def parse_general_intent_async(self, user_message: str) -> dict:
        """Async version of parse_general_intent for ASGI deployments."""
        import asyncio
        return await asyncio.to_thread(self.parse_general_intent, user_message)

    async def generate_explanation_async(
        self, 
        question_text: str, 
        user_answer: str, 
        correct_answer: str
    ) -> str:
        """Async version of generate_explanation for ASGI deployments."""
        import asyncio
        return await asyncio.to_thread(
            self.generate_explanation, question_text, user_answer, correct_answer
        )
