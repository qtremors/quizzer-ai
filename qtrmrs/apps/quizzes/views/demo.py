from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.conf import settings
from django_ratelimit.decorators import ratelimit
import logging
import random
from apps.quizzes.services import create_quiz_from_ai_data
from apps.ai_agent.models import AIModel
from apps.ai_agent.services import QuizGenerator, AIError

logger = logging.getLogger(__name__)

DEMO_TOPICS = [
    ('Python', 'Variables and Data Types'),
    ('Python', 'Functions and Arguments'),
    ('JavaScript', 'ES6 Arrow Functions'),
    ('JavaScript', 'Async/Await Basics'),
    ('SQL', 'SELECT Queries'),
    ('Git', 'Basic Commands'),
    ('CSS', 'Flexbox Basics'),
    ('HTML', 'Semantic Elements'),
]


@ratelimit(key='ip', rate='10/m', method='GET', block=True)
def quick_quiz(request):
    """
    One-click random quiz - works for both guests and logged-in users.
    Generates a 5-question quiz on a random topic.
    """
    language, topic = random.choice(DEMO_TOPICS)
    
    # Get default model - handle database errors specifically
    # Priority: 1. DB Default -> 2. Any DB Active -> 3. Settings/Env -> 4. Hardcoded
    default_model = AIModel.objects.filter(is_active=True, is_default=True).first()
    if not default_model:
        default_model = AIModel.objects.filter(is_active=True).first()
    if default_model:
        model_name = default_model.model_name
    else:
        model_name = settings.DEFAULT_AI_MODEL
        logger.warning(f"No active AI model found, using fallback: {model_name}")
    
    generator = QuizGenerator(model_name=model_name)
    
    logger.info(f"Quick Quiz: Generating {language} - {topic} with model {model_name}")
    
    questions_data = generator.generate_quiz(
        language=language, 
        topic=topic, 
        level='beginner',
        num_questions=5,
        include_code=False
    )
    
    # Handle AI error
    if isinstance(questions_data, AIError):
        logger.error(f"Quick Quiz AI Error: {questions_data.error_type} - {questions_data.message}")
        messages.error(request, f"Quiz generation failed: {questions_data.message}. {questions_data.suggestion}")
        return redirect('home')
    
    if not questions_data or len(questions_data) == 0:
        logger.error("Quick Quiz: Empty questions returned from AI")
        messages.error(request, "Quiz generation failed: No questions generated. Please try again.")
        return redirect('home')
    
    logger.info(f"Quick Quiz: Generated {len(questions_data)} questions successfully")
    
    if request.user.is_authenticated:
        # For logged-in users: save to database using shared service
        quiz = create_quiz_from_ai_data(
            request.user, questions_data,
            quiz_type='tech',
            language=language,
            topic_description=f"{language} - {topic}",
            difficulty='beginner',
            model_used=model_name,
        )
        
        return redirect('quiz_player', quiz_id=quiz.id)
    else:
        # For guests: store in session for demo mode
        # SEC-004: Limit session data size to prevent DoS
        MAX_DEMO_QUESTIONS = 10
        MAX_TEXT_LENGTH = 500
        
        # Optimize and limit session data
        optimized_questions = [
            {
                'text': q.get('text', '')[:MAX_TEXT_LENGTH],
                'options': q.get('options', [])[:6],  # Max 6 options
                'correct_answer': str(q.get('correct_answer', ''))[:255],
                'code_snippet': (q.get('code_snippet') or '')[:1000] if q.get('code_snippet') else None,
            }
            for q in questions_data[:MAX_DEMO_QUESTIONS]  # Limit questions
        ]
        request.session['demo_quiz'] = {
            'questions': optimized_questions,
            'topic': f"{language} - {topic}"[:100],
            'current_index': 0,
            'score': 0,
            'answers': [],
        }
        return redirect('demo_player')


@require_GET
def demo_player(request):
    """
    Demo quiz player for guests (session-based).
    No database storage - just session.
    """
    demo_quiz = request.session.get('demo_quiz')
    
    if not demo_quiz:
        return redirect('quick_quiz')
    
    questions = demo_quiz.get('questions', [])
    current_index = demo_quiz.get('current_index', 0)
    
    if current_index >= len(questions):
        # Quiz complete - show results
        return redirect('demo_results')
    
    question = questions[current_index]

    return render(request, 'quizzes/demo_player.html', {
        'question': question,
        'question_num': current_index + 1,
        'total_questions': len(questions),
        'topic': demo_quiz.get('topic'),
        'progress': ((current_index) / len(questions) * 100) if questions else 0,
    })


@require_http_methods(["POST"])
def demo_submit(request):
    """Handle demo quiz answer submission."""
    demo_quiz = request.session.get('demo_quiz')
    if not demo_quiz:
        return redirect('quick_quiz')
    
    questions = demo_quiz.get('questions', [])
    current_index = demo_quiz.get('current_index', 0)
    
    if current_index >= len(questions):
        return redirect('demo_results')
    
    question = questions[current_index]
    selected = request.POST.get('option', '')
    correct_answer = question.get('correct_answer', '')
    
    is_correct = str(selected) == str(correct_answer)
    
    # Update session
    demo_quiz['answers'].append({
        'question': question.get('text'),  # AI uses 'text' key
        'selected': selected,
        'correct': correct_answer,
        'is_correct': is_correct,
    })
    
    if is_correct:
        demo_quiz['score'] = demo_quiz.get('score', 0) + 1
    
    demo_quiz['current_index'] = current_index + 1
    request.session['demo_quiz'] = demo_quiz
    request.session.modified = True
    
    return redirect('demo_player')


@require_GET
def demo_results(request):
    """Show demo quiz results and prompt to sign up."""
    demo_quiz = request.session.get('demo_quiz')
    
    if not demo_quiz:
        return redirect('quick_quiz')
    
    questions = demo_quiz.get('questions', [])
    score = demo_quiz.get('score', 0)
    total = len(questions)
    score_percent = round((score / total * 100)) if total > 0 else 0
    
    context = {
        'topic': demo_quiz.get('topic'),
        'score': score,
        'total': total,
        'score_percent': score_percent,
        'answers': demo_quiz.get('answers', []),
    }
    
    # Clear demo quiz from session
    if 'demo_quiz' in request.session:
        del request.session['demo_quiz']
    
    return render(request, 'quizzes/demo_results.html', context)
