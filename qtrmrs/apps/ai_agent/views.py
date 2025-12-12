from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.db import transaction
from django.http import HttpResponse
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .services import QuizGenerator
from apps.quizzes.models import Quiz, Question, Option, AIModel


@login_required
@require_GET
def chat_interface(request):
    """Renders the general-purpose quiz chat page."""
    # Get available AI models for dropdown
    available_models = AIModel.objects.filter(is_active=True)
    default_model = available_models.filter(is_default=True).first()
    
    return render(request, 'ai_agent/chat.html', {
        'available_models': available_models,
        'default_model': default_model,
    })


@login_required
@ratelimit(key='user', rate='10/m', method='POST', block=True)
@require_http_methods(["POST"])
def process_chat_message(request):
    """
    General-purpose quiz generation from chat:
    1. Receives user message + settings
    2. Parses intent (Subject/Topic/Level)
    3. Generates general quiz
    4. Redirects to Player
    """
    user_message = request.POST.get('message', '')[:500]  # Limit message length
    
    if not user_message.strip():
        return HttpResponse("Please type something.", status=400)

    # Validate num_questions
    try:
        num_questions = int(request.POST.get('num_questions', 5))
        num_questions = min(max(num_questions, 1), 20)  # Clamp between 1-20
    except (ValueError, TypeError):
        num_questions = 5

    # --- Handle Model Selection ---
    model_id = request.POST.get('ai_model')
    ai_model = None
    model_name = getattr(settings, 'DEFAULT_AI_MODEL', 'gemini-2.0-flash-lite')
    
    if model_id:
        try:
            ai_model = AIModel.objects.get(id=model_id, is_active=True)
            model_name = ai_model.model_name
        except (AIModel.DoesNotExist, ValueError):
            pass
    
    generator = QuizGenerator(model_name=model_name)
    
    # 1. Parse Intent for general quiz
    params = generator.parse_general_intent(user_message)
    
    # Override with user's question count selection
    question_count = num_questions if num_questions else params.get('count', 5)
    
    # 2. Generate general-purpose quiz
    questions_data = generator.generate_general_quiz(
        subject=params.get('subject', 'General Knowledge')[:100],
        topic=params.get('topic', 'Trivia')[:200],
        level=params.get('level', 'Intermediate'),
        num_questions=question_count
    )

    # Handle errors with specific messages
    if not questions_data:
        from .services import AIError
        if isinstance(questions_data, AIError):
            return render(request, 'ai_agent/partials/chat_error.html', {
                'message': questions_data.message,
                'suggestion': questions_data.suggestion
            })
        return render(request, 'ai_agent/partials/chat_error.html', {
            'message': "I couldn't generate a quiz for that.",
            'suggestion': "Try being more specific or select a different AI model."
        })

    # 3. Save to DB
    with transaction.atomic():
        # Normalize difficulty to lowercase
        difficulty = params.get('level', 'Intermediate').lower()
        if difficulty not in ['beginner', 'intermediate', 'expert']:
            difficulty = 'intermediate'
        
        quiz = Quiz.objects.create(
            user=request.user,
            quiz_type='general',
            language=params.get('subject', 'General')[:50],
            topic_description=f"{params.get('subject')}: {params.get('topic')}"[:255],
            difficulty=difficulty,
            total_questions=len(questions_data),
            ai_model=ai_model,
            model_used=model_name
        )

        options_to_create = []
        for q_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=q_data.get('text', '')[:2000],
                code_snippet='',  # No code for general quizzes
                explanation=q_data.get('explanation', '')
            )
            
            for opt_text in q_data.get('options', []):
                options_to_create.append(Option(
                    question=question,
                    text=str(opt_text)[:255],
                    is_correct=(opt_text == q_data.get('correct_answer'))
                ))
        
        # Bulk create options
        if options_to_create:
            Option.objects.bulk_create(options_to_create)

    # 4. Redirect to Player
    response = HttpResponse()
    response['HX-Redirect'] = f"/quiz/play/{quiz.id}/"
    return response
