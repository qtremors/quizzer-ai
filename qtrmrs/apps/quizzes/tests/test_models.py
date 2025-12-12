"""
Tests for quiz models.
"""
import pytest
from django.db import IntegrityError
from apps.quizzes.models import AIModel, Quiz, Question, Option, UserAnswer


class TestAIModel:
    """Tests for AIModel."""
    
    def test_create_ai_model(self, db):
        """Test creating an AI model."""
        model = AIModel.objects.create(
            model_name='test-model',
            display_name='Test Model',
            is_active=True
        )
        assert model.model_name == 'test-model'
        assert model.display_name == 'Test Model'
        assert str(model) == 'Test Model'
    
    def test_only_one_default(self, db):
        """Test that only one model can be default."""
        model1 = AIModel.objects.create(
            model_name='model-1',
            display_name='Model 1',
            is_default=True,
            is_active=True
        )
        model2 = AIModel.objects.create(
            model_name='model-2',
            display_name='Model 2',
            is_default=True,  # This should unset model1
            is_active=True
        )
        
        model1.refresh_from_db()
        assert model1.is_default is False
        assert model2.is_default is True


class TestQuiz:
    """Tests for Quiz model."""
    
    def test_create_quiz(self, user, ai_model, db):
        """Test creating a quiz."""
        quiz = Quiz.objects.create(
            user=user,
            quiz_type='tech',
            language='Python',
            topic_description='Python basics',
            difficulty='beginner',
            total_questions=5,
            ai_model=ai_model
        )
        assert quiz.user == user
        assert quiz.language == 'Python'
        assert 'Python' in str(quiz)
    
    def test_quiz_defaults(self, user, db):
        """Test quiz default values."""
        quiz = Quiz.objects.create(
            user=user,
            language='JavaScript',
            topic_description='JS basics',
            difficulty='intermediate'
        )
        assert quiz.score == 0
        assert quiz.total_questions == 0


class TestUserAnswer:
    """Tests for UserAnswer model."""
    
    def test_unique_answer_per_question(self, quiz, db):
        """Test that duplicate answers for same question are prevented."""
        question = quiz.questions.first()
        option = question.options.first()
        
        # First answer should work
        UserAnswer.objects.create(
            quiz=quiz,
            question=question,
            selected_option=option,
            is_correct=False
        )
        
        # Second answer for same question should fail
        with pytest.raises(IntegrityError):
            UserAnswer.objects.create(
                quiz=quiz,
                question=question,
                selected_option=option,
                is_correct=False
            )
    
    def test_time_taken_tracking(self, quiz, db):
        """Test time tracking on answers."""
        question = quiz.questions.first()
        option = question.options.first()
        
        answer = UserAnswer.objects.create(
            quiz=quiz,
            question=question,
            selected_option=option,
            is_correct=False,
            time_taken=45
        )
        assert answer.time_taken == 45
