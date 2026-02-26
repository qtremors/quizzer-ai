"""
Tests for QuizGenerator class with mocked Gemini API.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from apps.ai_agent.services import QuizGenerator, AIError


# Sample AI response matching the expected JSON schema
MOCK_QUIZ_RESPONSE = json.dumps({
    "questions": [
        {
            "text": "What is a variable in Python?",
            "code_snippet": "",
            "options": ["A container for data", "A function", "A loop", "A class"],
            "correct_answer": "A container for data",
            "explanation": "Variables store data values."
        },
        {
            "text": "Which keyword defines a function?",
            "code_snippet": "def greet():\n    pass",
            "options": ["def", "func", "function", "define"],
            "correct_answer": "def",
            "explanation": "The 'def' keyword defines functions in Python."
        }
    ]
})

MOCK_GENERAL_QUIZ_RESPONSE = json.dumps({
    "questions": [
        {
            "text": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "Paris",
            "explanation": "Paris is the capital and largest city of France."
        }
    ]
})

MOCK_INTENT_RESPONSE = json.dumps({
    "language": "Python",
    "topic": "Decorators",
    "level": "Expert",
    "count": 10
})

MOCK_GENERAL_INTENT_RESPONSE = json.dumps({
    "subject": "History",
    "topic": "Ancient Rome",
    "level": "Intermediate",
    "count": 5
})


def _make_mock_response(text):
    """Create a mock Gemini API response object."""
    mock_response = MagicMock()
    mock_response.text = text
    return mock_response


@pytest.fixture
def mock_client():
    """Patch get_gemini_client to return a mock client."""
    with patch('apps.ai_agent.services.get_gemini_client') as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestQuizGeneratorInit:
    """Tests for QuizGenerator initialization."""
    
    def test_init_default_model(self, mock_client, settings):
        """Default model comes from Django settings."""
        settings.DEFAULT_AI_MODEL = 'test-model'
        gen = QuizGenerator()
        assert gen.model_name == 'test-model'
    
    def test_init_custom_model(self, mock_client):
        """Custom model name is stored."""
        gen = QuizGenerator(model_name='custom-model-v2')
        assert gen.model_name == 'custom-model-v2'


class TestGenerateQuiz:
    """Tests for programming quiz generation."""
    
    def test_generate_quiz_success(self, mock_client):
        """Valid JSON response returns list of question dicts."""
        mock_client.models.generate_content.return_value = _make_mock_response(MOCK_QUIZ_RESPONSE)
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_quiz(language='Python', topic='Variables', level='beginner')
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['text'] == "What is a variable in Python?"
        assert result[0]['correct_answer'] == "A container for data"
    
    def test_generate_quiz_with_code(self, mock_client):
        """include_code=True passes code instruction to prompt."""
        mock_client.models.generate_content.return_value = _make_mock_response(MOCK_QUIZ_RESPONSE)
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_quiz(
            language='Python', topic='Functions', level='intermediate',
            include_code=True
        )
        
        # Verify the prompt contained code instruction
        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get('contents', call_args[1].get('contents', ''))
        assert 'MUST include a relevant code snippet' in prompt
        assert isinstance(result, list)
    
    def test_generate_quiz_returns_ai_error_on_exception(self, mock_client):
        """API exception returns AIError instead of raising."""
        mock_client.models.generate_content.side_effect = Exception("Connection refused")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_quiz(language='Python', topic='Variables', level='beginner')
        
        assert isinstance(result, AIError)
        assert not result  # AIError is falsy
    
    def test_generate_quiz_json_parse_error(self, mock_client):
        """Malformed JSON response returns AIError."""
        mock_client.models.generate_content.return_value = _make_mock_response("not valid json{{{")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_quiz(language='Python', topic='Variables', level='beginner')
        
        assert isinstance(result, AIError)


class TestGenerateGeneralQuiz:
    """Tests for general-purpose quiz generation."""
    
    def test_generate_general_quiz_success(self, mock_client):
        """Valid JSON response returns list of question dicts."""
        mock_client.models.generate_content.return_value = _make_mock_response(MOCK_GENERAL_QUIZ_RESPONSE)
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_general_quiz(subject='Geography', topic='Capitals', level='Beginner')
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['correct_answer'] == "Paris"
    
    def test_generate_general_quiz_returns_ai_error(self, mock_client):
        """API exception returns AIError."""
        mock_client.models.generate_content.side_effect = Exception("500 Server Error")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_general_quiz(subject='History', topic='Rome', level='Beginner')
        
        assert isinstance(result, AIError)


class TestParseIntent:
    """Tests for intent parsing."""
    
    def test_parse_intent_success(self, mock_client):
        """Returns parsed language/topic/level/count."""
        mock_client.models.generate_content.return_value = _make_mock_response(MOCK_INTENT_RESPONSE)
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.parse_intent("Give me 10 expert Python decorator questions")
        
        assert result['language'] == 'Python'
        assert result['topic'] == 'Decorators'
        assert result['level'] == 'Expert'
        assert result['count'] == 10
    
    def test_parse_intent_fallback_on_error(self, mock_client):
        """On API error, returns default dict."""
        mock_client.models.generate_content.side_effect = Exception("API Error")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.parse_intent("broken request")
        
        assert result['language'] == 'General'
        assert result['topic'] == 'Random'
        assert result['level'] == 'Intermediate'
        assert result['count'] == 5
    
    def test_parse_general_intent_success(self, mock_client):
        """Returns parsed subject/topic/level/count."""
        mock_client.models.generate_content.return_value = _make_mock_response(MOCK_GENERAL_INTENT_RESPONSE)
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.parse_general_intent("Quiz me on Ancient Rome")
        
        assert result['subject'] == 'History'
        assert result['topic'] == 'Ancient Rome'
    
    def test_parse_general_intent_fallback_on_error(self, mock_client):
        """On API error, returns default dict."""
        mock_client.models.generate_content.side_effect = Exception("Timeout")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.parse_general_intent("broken request")
        
        assert result['subject'] == 'General Knowledge'
        assert result['topic'] == 'Trivia'


class TestGenerateExplanation:
    """Tests for explanation generation."""
    
    def test_generate_explanation_success(self, mock_client):
        """Returns explanation string."""
        mock_client.models.generate_content.return_value = _make_mock_response(
            "The correct answer is 'def' because it is Python's function keyword."
        )
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_explanation(
            question_text="Which keyword?",
            user_answer="func",
            correct_answer="def"
        )
        
        assert isinstance(result, str)
        assert 'def' in result
    
    def test_generate_explanation_quota_error(self, mock_client):
        """429 error returns quota message."""
        mock_client.models.generate_content.side_effect = Exception("429 Resource Exhausted: quota exceeded")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_explanation(
            question_text="Q?",
            user_answer="A",
            correct_answer="B"
        )
        
        assert 'quota' in result.lower()
