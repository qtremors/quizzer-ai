from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .models import Quiz, Question, Option, UserAnswer, AIModel
from apps.ai_agent.services import QuizGenerator

# ==========================================
# 1. QUIZ SETUP & CREATION
# ==========================================

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
    model_name = getattr(settings, 'DEFAULT_AI_MODEL', 'gemini-2.0-flash-lite')
    
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
        from apps.ai_agent.services import AIError
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

    with transaction.atomic():
        quiz = Quiz.objects.create(
            user=request.user,
            quiz_type='tech',
            language=language,
            topic_description=f"{language}: {topic}"[:255],
            difficulty=level,
            total_questions=len(questions_data),
            ai_model=ai_model,
            model_used=model_name
        )

        options_to_create = []
        for q_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=q_data.get('text', '')[:2000],
                code_snippet=q_data.get('code_snippet', ''),
                explanation=q_data.get('explanation', '')
            )
            # Prepare options for bulk creation
            for opt_text in q_data.get('options', []):
                options_to_create.append(Option(
                    question=question,
                    text=str(opt_text)[:255],
                    is_correct=(str(opt_text) == str(q_data.get('correct_answer', '')))
                ))
        
        # Bulk create all options at once
        if options_to_create:
            Option.objects.bulk_create(options_to_create)

    response = HttpResponse()
    response['HX-Redirect'] = f"/quiz/play/{quiz.id}/"
    return response


# ==========================================
# 2. CLASSIC EXAM PLAYER
# ==========================================

@login_required
@require_GET
def quiz_player(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    answered_ids = list(quiz.answers.values_list('question_id', flat=True))
    current_question = quiz.questions.exclude(id__in=answered_ids).first()

    if not current_question:
        return redirect('quiz_results', quiz_id=quiz.id)

    total_qs = quiz.questions.count()
    # Avoid division by zero
    progress = (len(answered_ids) / total_qs * 100) if total_qs > 0 else 0

    return render(request, 'quizzes/player.html', {
        'quiz': quiz,
        'current_question': current_question,
        'progress': progress,
        'is_last': (len(answered_ids) + 1 == total_qs)
    })

@login_required
@require_http_methods(["POST"])
def submit_answer(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    # Check if answer already exists (prevent duplicate submissions)
    if UserAnswer.objects.filter(quiz=quiz, question=question).exists():
        # Already answered, just get next question
        answered_ids = list(quiz.answers.values_list('question_id', flat=True))
        next_q = quiz.questions.exclude(id__in=answered_ids).first()
        
        if not next_q:
            response = HttpResponse()
            response['HX-Redirect'] = f"/quiz/results/{quiz.id}/"
            return response
        
        total_qs = quiz.questions.count()
        progress = (len(answered_ids) / total_qs * 100) if total_qs > 0 else 0
        
        return render(request, 'quizzes/partials/question_card.html', {
            'quiz': quiz,
            'question': next_q,
            'progress': progress,
            'is_last': (len(answered_ids) + 1 == total_qs)
        })
    
    selected_option_id = request.POST.get('option')
    action = request.POST.get('action')
    
    # Get time taken (in seconds)
    try:
        time_taken = int(request.POST.get('time_taken', 0))
        time_taken = min(max(time_taken, 0), 3600)  # Clamp 0-1hr
    except (ValueError, TypeError):
        time_taken = 0
    
    # Create the answer
    if action == 'skip' or not selected_option_id:
        user_answer = UserAnswer.objects.create(
            quiz=quiz, question=question, selected_option=None, 
            is_correct=False, time_taken=time_taken
        )
    else:
        selected_option = get_object_or_404(Option, id=selected_option_id, question=question)
        is_correct = selected_option.is_correct
        user_answer = UserAnswer.objects.create(
            quiz=quiz, question=question, selected_option=selected_option, 
            is_correct=is_correct, time_taken=time_taken
        )

    # Get next question
    answered_ids = list(quiz.answers.values_list('question_id', flat=True))
    next_q = quiz.questions.exclude(id__in=answered_ids).first()

    if not next_q:
        # Quiz completed - calculate final score properly
        correct_count = quiz.answers.filter(is_correct=True).count()
        total_qs = quiz.total_questions
        quiz.score = round((correct_count / total_qs * 100)) if total_qs > 0 else 0
        quiz.completed_at = timezone.now()
        quiz.save()
        
        # === GAMIFICATION: Award XP, update streak, check badges ===
        from apps.users.gamification import (
            calculate_quiz_xp, calculate_level_from_xp, 
            update_user_streak, check_and_award_badges
        )
        from django.contrib import messages
        
        # Get user profile
        profile = request.user.profile
        old_level = profile.level
        
        # Calculate and award XP
        total_time = sum(a.time_taken for a in quiz.answers.all())
        xp_earned = calculate_quiz_xp(correct_count, total_time, total_qs)
        profile.xp += xp_earned
        
        # Check for level up
        new_level = calculate_level_from_xp(profile.xp)
        leveled_up = new_level > old_level
        profile.level = new_level
        
        # Update streak
        update_user_streak(profile)
        
        # Update cached stats
        profile.total_correct_answers += correct_count
        profile.total_study_time += total_time
        if quiz.score > profile.best_score:
            profile.best_score = quiz.score
        
        profile.save()
        
        # Check and award badges
        new_badges = check_and_award_badges(request.user, profile)
        
        # Store XP info in session for display on results page
        request.session['quiz_xp_earned'] = xp_earned
        request.session['quiz_leveled_up'] = leveled_up
        request.session['quiz_new_level'] = new_level if leveled_up else None
        request.session['quiz_new_badges'] = [b.name for b in new_badges] if new_badges else []
        
        response = HttpResponse()
        response['HX-Redirect'] = f"/quiz/results/{quiz.id}/"
        return response

    total_qs = quiz.questions.count()
    progress = (len(answered_ids) / total_qs * 100) if total_qs > 0 else 0
    
    return render(request, 'quizzes/partials/question_card.html', {
        'quiz': quiz,
        'question': next_q,
        'progress': progress,
        'is_last': (len(answered_ids) + 1 == total_qs)
    })

@login_required
@require_GET
def quiz_results(request, quiz_id):
    """Renders the results page."""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    user_answers = UserAnswer.objects.filter(quiz=quiz).select_related('question', 'selected_option')
    
    correct_count = user_answers.filter(is_correct=True).count()
    skipped_count = user_answers.filter(selected_option__isnull=True).count()
    wrong_count = quiz.total_questions - correct_count - skipped_count
    
    # Recalculate score if needed (in case it wasn't set properly)
    if quiz.score == 0 and correct_count > 0:
        quiz.score = round((correct_count / quiz.total_questions * 100)) if quiz.total_questions > 0 else 0
        quiz.save(update_fields=['score'])
    
    # Check if any explanations generated yet
    has_explanations = user_answers.exclude(error_explanation='').exists()
    
    # Calculate time statistics
    total_time = sum(a.time_taken for a in user_answers)
    avg_time = round(total_time / len(user_answers)) if user_answers else 0
    
    # Format total time as MM:SS or just seconds
    if total_time >= 60:
        minutes = total_time // 60
        seconds = total_time % 60
        total_time_formatted = f"{minutes}m {seconds}s"
    else:
        total_time_formatted = f"{total_time}s"

    # Get XP info from session (set during quiz completion)
    xp_earned = request.session.pop('quiz_xp_earned', None)
    leveled_up = request.session.pop('quiz_leveled_up', False)
    new_level = request.session.pop('quiz_new_level', None)
    new_badges = request.session.pop('quiz_new_badges', [])

    return render(request, 'quizzes/results.html', {
        'quiz': quiz,
        'user_answers': user_answers,
        'score_percent': int(quiz.score),
        'correct': correct_count,
        'skipped': skipped_count,
        'wrong': wrong_count,
        'has_explanations': has_explanations,
        'total_time': total_time,
        'total_time_formatted': total_time_formatted,
        'avg_time': avg_time,
        # Gamification
        'xp_earned': xp_earned,
        'leveled_up': leveled_up,
        'new_level': new_level,
        'new_badges': new_badges,
        'profile': request.user.profile,
    })

@login_required
@require_http_methods(["POST"])
def generate_all_explanations(request, quiz_id):
    """
    HTMX View: 
    1. Finds ALL wrong/skipped answers.
    2. Generates AI text for them in a batch (loop).
    3. Re-renders the answer list part of the page with explanations included.
    Uses the same AI model that was used to generate the quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    # Filter for wrong or skipped answers that don't have an explanation yet
    # (is_correct=False covers both Wrong and Skipped)
    # prefetch_related avoids N+1 query when accessing options in the loop
    answers_needing_help = UserAnswer.objects.filter(
        quiz=quiz, 
        is_correct=False, 
        error_explanation=''
    ).select_related('question', 'selected_option').prefetch_related('question__options')
    
    # Use the same model that generated this quiz
    model_to_use = quiz.model_used if quiz.model_used else None
    generator = QuizGenerator(model_name=model_to_use)
    
    for ans in answers_needing_help:
        # Use Python filtering instead of DB query to leverage prefetch
        correct_opt = next((o for o in ans.question.options.all() if o.is_correct), None)
        user_text = ans.selected_option.text if ans.selected_option else "Skipped"
        
        explanation = generator.generate_explanation(
            question_text=ans.question.text,
            user_answer=user_text,
            correct_answer=correct_opt.text if correct_opt else "Unknown"
        )
        ans.error_explanation = explanation
        ans.save(update_fields=['error_explanation'])
    
    # Re-fetch all answers to render the list again
    user_answers = UserAnswer.objects.filter(quiz=quiz).select_related(
        'question', 'selected_option'
    ).prefetch_related('question__options')
    
    # We render a partial template that just contains the list loop
    return render(request, 'quizzes/partials/results_list.html', {'user_answers': user_answers})


@login_required
@require_http_methods(["POST"])
def retry_quiz(request, quiz_id):
    """
    Resets a quiz so the user can retake it.
    - Deletes all UserAnswer records
    - Resets score and completed_at
    - Redirects to the quiz player
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    # Delete all existing answers
    quiz.answers.all().delete()
    
    # Reset quiz state
    quiz.score = 0
    quiz.completed_at = None
    quiz.save(update_fields=['score', 'completed_at'])
    
    return redirect('quiz_player', quiz_id=quiz.id)


# ==========================================
# 6. QUICK QUIZ (DEMO MODE)
# ==========================================

import random

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
    
    # Get default model
    try:
        default_model = AIModel.objects.filter(is_active=True).first()
        model_name = default_model.model_id if default_model else 'gemini-2.0-flash'
    except:
        model_name = 'gemini-2.0-flash'
    
    generator = QuizGenerator(model_name=model_name)
    questions_data = generator.generate_quiz(
        language=language, 
        topic=topic, 
        level='Easy', 
        num_questions=5,
        include_code=False
    )
    
    # Handle AI error
    from apps.ai_agent.services import AIError
    if isinstance(questions_data, AIError):
        from django.contrib import messages
        messages.error(request, f"Quiz generation failed: {questions_data.message}")
        return redirect('home')
    
    if request.user.is_authenticated:
        # For logged-in users: save to database like normal
        with transaction.atomic():
            quiz = Quiz.objects.create(
                user=request.user,
                topic_description=f"{language} - {topic}",
                difficulty='Easy',
                total_questions=len(questions_data),
                model_used=model_name,
            )
            
            for q_data in questions_data:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data.get('question', ''),
                    code_snippet=q_data.get('code_snippet'),
                    code_language=language.lower() if q_data.get('code_snippet') else None
                )
                
                for option_data in q_data.get('options', []):
                    Option.objects.create(
                        question=question,
                        text=str(option_data.get('text', '')),
                        is_correct=(str(option_data.get('text', '')) == str(q_data.get('correct_answer', '')))
                    )
        
        return redirect('quiz_player', quiz_id=quiz.id)
    else:
        # For guests: store in session for demo mode
        request.session['demo_quiz'] = {
            'questions': questions_data,
            'topic': f"{language} - {topic}",
            'current_index': 0,
            'score': 0,
            'answers': [],
        }
        return redirect('demo_player')


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


def demo_submit(request):
    """Handle demo quiz answer submission."""
    if request.method != 'POST':
        return redirect('demo_player')
    
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
        'question': question.get('question'),
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
