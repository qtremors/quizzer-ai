"""
Tests for AI error handling — _handle_error classification and AIError behavior.
"""
import pytest
from unittest.mock import patch, MagicMock
from apps.ai_agent.services import QuizGenerator, AIError


@pytest.fixture
def mock_client():
    """Patch get_gemini_client to return a mock client."""
    with patch('apps.ai_agent.services.get_gemini_client') as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestAIError:
    """Tests for AIError class behavior."""
    
    def test_ai_error_is_falsy(self):
        """AIError evaluates as False (allows `if not result` patterns)."""
        error = AIError(error_type='test', message='test error')
        assert not error
        assert bool(error) is False
    
    def test_ai_error_stores_fields(self):
        """AIError stores error_type, message, and suggestion."""
        error = AIError(
            error_type='quota',
            message='Rate limited',
            suggestion='Wait and retry'
        )
        assert error.error_type == 'quota'
        assert error.message == 'Rate limited'
        assert error.suggestion == 'Wait and retry'
    
    def test_ai_error_default_suggestion(self):
        """Suggestion defaults to empty string."""
        error = AIError(error_type='test', message='msg')
        assert error.suggestion == ''


class TestHandleError:
    """Tests for _handle_error error classification."""
    
    def test_handle_error_quota_429(self, mock_client):
        """429 status code maps to 'quota' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("429 Resource Exhausted"), "Test")
        
        assert isinstance(result, AIError)
        assert result.error_type == 'quota'
    
    def test_handle_error_quota_keyword(self, mock_client):
        """'quota' keyword in message maps to 'quota' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("API quota exceeded"), "Test")
        
        assert result.error_type == 'quota'
    
    def test_handle_error_rate_keyword(self, mock_client):
        """'rate' keyword in message maps to 'quota' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("rate limit exceeded"), "Test")
        
        assert result.error_type == 'quota'
    
    def test_handle_error_not_found_404(self, mock_client):
        """404 status code maps to 'model_not_found' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("404 Not Found"), "Test")
        
        assert result.error_type == 'model_not_found'
    
    def test_handle_error_not_found_keyword(self, mock_client):
        """'not found' keyword maps to 'model_not_found' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Model not found in registry"), "Test")
        
        assert result.error_type == 'model_not_found'
    
    def test_handle_error_auth_403(self, mock_client):
        """403 status code maps to 'auth' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("403 Forbidden"), "Test")
        
        assert result.error_type == 'auth'
    
    def test_handle_error_permission_keyword(self, mock_client):
        """'permission' keyword maps to 'auth' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Permission denied"), "Test")
        
        assert result.error_type == 'auth'
    
    def test_handle_error_api_key_keyword(self, mock_client):
        """'api key' keyword maps to 'auth' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Invalid API key provided"), "Test")
        
        assert result.error_type == 'auth'
    
    def test_handle_error_timeout(self, mock_client):
        """'timeout' keyword maps to 'timeout' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Connection timeout"), "Test")
        
        assert result.error_type == 'timeout'
    
    def test_handle_error_deadline(self, mock_client):
        """'deadline' keyword maps to 'timeout' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Deadline exceeded"), "Test")
        
        assert result.error_type == 'timeout'
    
    def test_handle_error_unknown(self, mock_client):
        """Generic exception maps to 'unknown' error type."""
        gen = QuizGenerator(model_name='test-model')
        result = gen._handle_error(Exception("Something completely unexpected"), "Test")
        
        assert result.error_type == 'unknown'
    
    def test_handle_error_includes_model_name(self, mock_client):
        """Quota error message includes the model name."""
        gen = QuizGenerator(model_name='gemini-pro-latest')
        result = gen._handle_error(Exception("429 quota"), "Test")
        
        assert 'gemini-pro-latest' in result.message


class TestErrorPropagation:
    """Tests that errors propagate correctly through public methods."""
    
    def test_generate_quiz_propagates_quota_error(self, mock_client):
        """Quota error from API returns appropriate AIError from generate_quiz."""
        mock_client.models.generate_content.side_effect = Exception("429 quota exceeded")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_quiz(language='Python', topic='Test', level='beginner')
        
        assert isinstance(result, AIError)
        assert result.error_type == 'quota'
    
    def test_generate_general_quiz_propagates_error(self, mock_client):
        """Error from API returns AIError from generate_general_quiz."""
        mock_client.models.generate_content.side_effect = Exception("404 model not found")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_general_quiz(subject='Test', topic='Test', level='beginner')
        
        assert isinstance(result, AIError)
        assert result.error_type == 'model_not_found'
    
    def test_generate_explanation_generic_error(self, mock_client):
        """Non-quota error returns generic fallback string."""
        mock_client.models.generate_content.side_effect = Exception("Network unreachable")
        
        gen = QuizGenerator(model_name='test-model')
        result = gen.generate_explanation(
            question_text="Q?", user_answer="A", correct_answer="B"
        )
        
        assert isinstance(result, str)
        assert 'unable' in result.lower()
