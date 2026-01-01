"""
Pytest fixtures for Quizzer AI tests.
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a logged-in test client."""
    client.login(email='test@example.com', password='testpass123')
    return client


@pytest.fixture
def ai_model(db):
    """Create a test AI model."""
    from apps.quizzes.models import AIModel
    return AIModel.objects.create(
        model_name='gemini-flash-latest',
        display_name='Gemini Flash (Latest)',
        is_default=True,
        is_active=True
    )


@pytest.fixture
def quiz(db, user, ai_model):
    """Create a test quiz with questions and options."""
    from apps.quizzes.models import Quiz, Question, Option
    
    quiz = Quiz.objects.create(
        user=user,
        quiz_type='tech',
        language='Python',
        topic_description='Python: Variables',
        difficulty='intermediate',
        total_questions=2,
        ai_model=ai_model,
        model_used='gemini-flash-latest'
    )
    
    # Create questions with options
    q1 = Question.objects.create(
        quiz=quiz,
        text='What keyword is used to define a variable in Python?',
        explanation='In Python, variables are created by assignment.'
    )
    Option.objects.create(question=q1, text='var', is_correct=False)
    Option.objects.create(question=q1, text='let', is_correct=False)
    Option.objects.create(question=q1, text='No keyword needed', is_correct=True)
    Option.objects.create(question=q1, text='dim', is_correct=False)
    
    q2 = Question.objects.create(
        quiz=quiz,
        text='What is the output of print(type(5))?',
        explanation="The type() function returns the class type of an object."
    )
    Option.objects.create(question=q2, text='int', is_correct=False)
    Option.objects.create(question=q2, text="<class 'int'>", is_correct=True)
    Option.objects.create(question=q2, text='5', is_correct=False)
    Option.objects.create(question=q2, text='number', is_correct=False)
    
    return quiz
