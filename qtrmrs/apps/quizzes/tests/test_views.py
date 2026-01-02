"""
Tests for quiz views.
"""
import pytest
from django.urls import reverse


class TestQuizSetup:
    """Tests for quiz setup view."""
    
    def test_setup_requires_login(self, client):
        """Test that setup page requires authentication."""
        response = client.get(reverse('quiz_setup'))
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_setup_page_loads(self, authenticated_client, ai_model):
        """Test that setup page loads for authenticated user."""
        response = authenticated_client.get(reverse('quiz_setup'))
        assert response.status_code == 200
        assert b'Configure Session' in response.content


class TestQuizPlayer:
    """Tests for quiz player view."""
    
    def test_player_requires_login(self, client, quiz):
        """Test that player requires authentication."""
        response = client.get(reverse('quiz_player', args=[quiz.id]))
        assert response.status_code == 302
    
    def test_player_loads_own_quiz(self, authenticated_client, quiz):
        """Test that user can access their own quiz."""
        response = authenticated_client.get(reverse('quiz_player', args=[quiz.id]))
        assert response.status_code == 200
        assert quiz.topic_description.encode() in response.content


class TestSubmitAnswer:
    """Tests for answer submission."""
    
    def test_submit_answer(self, authenticated_client, quiz, db):
        """Test submitting an answer."""
        question = quiz.questions.first()
        option = question.options.filter(is_correct=True).first()
        
        response = authenticated_client.post(
            reverse('submit_answer', args=[quiz.id, question.id]),
            {'option': option.id, 'action': 'next', 'time_taken': '10'}
        )
        
        # Should return partial HTML for next question
        assert response.status_code == 200
    
    def test_skip_answer(self, authenticated_client, quiz, db):
        """Test skipping a question."""
        question = quiz.questions.first()
        
        response = authenticated_client.post(
            reverse('submit_answer', args=[quiz.id, question.id]),
            {'action': 'skip', 'time_taken': '5'}
        )
        
        assert response.status_code == 200
        
        # Check answer was created as skipped
        from apps.quizzes.models import UserAnswer
        answer = UserAnswer.objects.get(quiz=quiz, question=question)
        assert answer.selected_option is None
        assert answer.is_correct is False


class TestQuizResults:
    """Tests for results view."""
    
    def test_results_requires_login(self, client, quiz):
        """Test results page requires auth."""
        response = client.get(reverse('quiz_results', args=[quiz.id]))
        assert response.status_code == 302
    
    def test_results_shows_score(self, authenticated_client, quiz, db):
        """Test results page shows score."""
        # Complete the quiz first
        for question in quiz.questions.all():
            correct_option = question.options.filter(is_correct=True).first()
            authenticated_client.post(
                reverse('submit_answer', args=[quiz.id, question.id]),
                {'option': correct_option.id, 'action': 'next', 'time_taken': '10'}
            )
        
        # Check results
        response = authenticated_client.get(reverse('quiz_results', args=[quiz.id]))
        assert response.status_code == 200
        # Should show 100% for all correct
        assert b'100%' in response.content


class TestQuizDeletion:
    """Tests for quiz deletion."""
    
    def test_delete_requires_login(self, client, quiz):
        """Test delete requires authentication."""
        response = client.post(reverse('delete_quiz', args=[quiz.id]))
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_delete_own_quiz(self, authenticated_client, quiz, db):
        """Test user can delete their own quiz."""
        quiz_id = quiz.id
        response = authenticated_client.post(reverse('delete_quiz', args=[quiz_id]))
        
        # Should redirect to dashboard
        assert response.status_code == 302
        
        # Quiz should be deleted
        from apps.quizzes.models import Quiz
        assert not Quiz.objects.filter(id=quiz_id).exists()
    
    def test_cannot_delete_others_quiz(self, client, quiz, db):
        """Test user cannot delete another user's quiz."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create and login as different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        client.login(email='other@example.com', password='testpass123')
        
        response = client.post(reverse('delete_quiz', args=[quiz.id]))
        # Should get 404 since quiz doesn't belong to this user
        assert response.status_code == 404


class TestQuizRetry:
    """Tests for quiz retry functionality."""
    
    def test_retry_requires_login(self, client, quiz):
        """Test retry requires authentication."""
        response = client.post(reverse('retry_quiz', args=[quiz.id]))
        assert response.status_code == 302
    
    def test_retry_resets_quiz(self, authenticated_client, quiz, db):
        """Test retry clears answers and resets quiz."""
        from apps.quizzes.models import UserAnswer
        
        # First, add an answer
        question = quiz.questions.first()
        option = question.options.first()
        authenticated_client.post(
            reverse('submit_answer', args=[quiz.id, question.id]),
            {'option': option.id, 'action': 'next', 'time_taken': '10'}
        )
        
        # Verify answer exists
        assert UserAnswer.objects.filter(quiz=quiz).exists()
        
        # Retry the quiz
        response = authenticated_client.post(reverse('retry_quiz', args=[quiz.id]))
        
        # Should redirect to player
        assert response.status_code == 302
        
        # Answers should be cleared
        assert not UserAnswer.objects.filter(quiz=quiz).exists()


class TestXPTracking:
    """Tests for XP and gamification tracking."""
    
    def test_xp_awarded_once(self, authenticated_client, quiz, user, db):
        """Test XP is only awarded once per quiz."""
        # Complete quiz
        for question in quiz.questions.all():
            correct_option = question.options.filter(is_correct=True).first()
            authenticated_client.post(
                reverse('submit_answer', args=[quiz.id, question.id]),
                {'option': correct_option.id, 'action': 'next', 'time_taken': '10'}
            )
        
        # Check XP was awarded
        user.profile.refresh_from_db()
        xp_after_first = user.profile.xp
        assert xp_after_first > 0
        
        # Quiz should be marked as xp_awarded
        quiz.refresh_from_db()
        assert quiz.xp_awarded is True

