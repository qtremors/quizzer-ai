from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.utils import timezone
from apps.quizzes.models import Quiz, Question, Option, UserAnswer
from apps.quizzes.services import award_quiz_completion


@login_required
@require_GET
def quiz_player(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    answered_ids = list(quiz.answers.values_list('question_id', flat=True))
    current_question = quiz.questions.exclude(id__in=answered_ids).first()

    if not current_question:
        return redirect('quiz_results', quiz_id=quiz.id)

    total_qs = quiz.total_questions
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
    """
    HTMX POST handler: records the user's answer, advances to the next question,
    and triggers scoring + gamification when the quiz is complete.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    # PERF-009: Invalidate dashboard cache for this user since a quiz action occurred
    from django.core.cache import cache
    cache.delete(f'user_dashboard_stats_{request.user.id}')
    
    # Check if answer already exists (prevent duplicate submissions)
    if not UserAnswer.objects.filter(quiz=quiz, question=question).exists():
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

    # PERF-009: Consolidate getting the list of answered IDs to exactly once.
    answered_ids = list(quiz.answers.values_list('question_id', flat=True))
    next_q = quiz.questions.exclude(id__in=answered_ids).first()

    if not next_q:
        # BUG-010: Only check completed_at — xp_awarded flag inside award_quiz_completion
        # already prevents double-awarding. Old guard `quiz.score == 0` broke retried quizzes.
        if not quiz.completed_at:
            # Quiz completed - calculate final score properly
            correct_count = quiz.answers.filter(is_correct=True).count()
            total_qs = quiz.total_questions
            quiz.score = round((correct_count / total_qs * 100)) if total_qs > 0 else 0
            quiz.completed_at = timezone.now()
            
            # Gamification: XP, levels, streaks, badges
            # BUG-012: award_quiz_completion already saves score/completed_at/xp_awarded
            # via locked_quiz.save() — do NOT call quiz.save() here to avoid overwriting.
            gamification = award_quiz_completion(quiz, request.user)
            
            # Store XP info in session for display on results page
            request.session['quiz_xp_earned'] = gamification['xp_earned']
            request.session['quiz_leveled_up'] = gamification['leveled_up']
            request.session['quiz_new_level'] = gamification['new_level']
            request.session['quiz_new_badges'] = (
                [b.name for b in gamification['new_badges']] if gamification['new_badges'] else []
            )
        
        response = HttpResponse()
        response['HX-Redirect'] = f"/quiz/results/{quiz.id}/"
        return response

    total_qs = quiz.total_questions
    progress = (len(answered_ids) / total_qs * 100) if total_qs > 0 else 0
    
    return render(request, 'quizzes/partials/question_card.html', {
        'quiz': quiz,
        'question': next_q,
        'progress': progress,
        'is_last': (len(answered_ids) + 1 == total_qs)
    })
