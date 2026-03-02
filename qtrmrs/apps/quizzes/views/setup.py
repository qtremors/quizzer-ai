from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from apps.quizzes.models import Quiz
from apps.quizzes.services import create_quiz_from_ai_data
from apps.ai_agent.models import AIModel
from apps.ai_agent.services import QuizGenerator, AIError


@login_required
@require_GET
def quiz_setup(request):
    """Renders the quiz configuration page."""
    # Capture URL param e.g. /quiz/setup/?language=python
    initial_lang = request.GET.get('language', '')
    
    # Get available AI models for dropdown
    available_models = AIModel.objects.filter(is_active=True)
    default_model = available_models.filter(is_default=True).first()
    
    return render(request, 'quizzes/setup.html', {
        'initial_lang': initial_lang,
        'available_models': available_models,
        'default_model': default_model,
    })

@login_required
@ratelimit(key='user', rate='10/m', method='POST', block=True)
@require_http_methods(["POST"])
def create_quiz(request):
    """
    HTMX POST handler: validates form input, calls AI to generate questions,
    saves the quiz via create_quiz_from_ai_data, and redirects to the player.
    """
    # --- Input Validation ---
    topic = request.POST.get('topic', '')[:255]  # Limit length
    if not topic.strip():
        return render(request, 'quizzes/partials/error_alert.html', {
            'message': "Please enter a topic."
        })
    
    # --- Handle Custom Language Logic ---
    lang_select = request.POST.get('language_select', 'Python')
    custom_lang = request.POST.get('custom_language', '')
    
    # If custom_lang has text, USE IT. Else, use dropdown.
    language = custom_lang.strip()[:50] if custom_lang and custom_lang.strip() else lang_select[:50]
    
    # Normalize difficulty to lowercase
    level = request.POST.get('level', 'intermediate').lower()
    if level not in ['beginner', 'intermediate', 'expert']:
        level = 'intermediate'
    
    # Validate num_questions
    try:
        num_questions = int(request.POST.get('num_questions', 5))
        num_questions = min(max(num_questions, 1), 20)  # Clamp between 1-20
    except (ValueError, TypeError):
        num_questions = 5
    
    include_code = request.POST.get('include_code') == 'on'
    
    # --- Handle Model Selection ---
    model_id = request.POST.get('ai_model')
    ai_model = None
    model_name = settings.DEFAULT_AI_MODEL
    
    if model_id:
        try:
            ai_model = AIModel.objects.get(id=model_id, is_active=True)
            model_name = ai_model.model_name
        except (AIModel.DoesNotExist, ValueError):
            pass
    
    generator = QuizGenerator(model_name=model_name)
    
    # Generate the quiz
    questions_data = generator.generate_quiz(
        language=language, 
        topic=topic, 
        level=level, 
        num_questions=num_questions,
        include_code=include_code
    )

    # Handle errors with specific messages
    if not questions_data:
        if isinstance(questions_data, AIError):
            return render(request, 'quizzes/partials/error_alert.html', {
                'message': questions_data.message,
                'suggestion': questions_data.suggestion,
                'error_type': questions_data.error_type
            })
        return render(request, 'quizzes/partials/error_alert.html', {
            'message': "AI failed to generate quiz.",
            'suggestion': "Try again or select a different AI model."
        })

    quiz = create_quiz_from_ai_data(
        request.user, questions_data,
        quiz_type='tech',
        language=language,
        topic_description=f"{language}: {topic}",
        difficulty=level,
        ai_model=ai_model,
        model_used=model_name
    )

    response = HttpResponse()
    response['HX-Redirect'] = f"/quiz/play/{quiz.id}/"
    return response
