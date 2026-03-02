from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from apps.quizzes.models import Quiz, UserAnswer
from apps.quizzes.utils import format_duration
from apps.ai_agent.services import QuizGenerator


@login_required
@require_GET
def quiz_results(request, quiz_id):
    """Renders the results page."""
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    user_answers = UserAnswer.objects.filter(quiz=quiz).select_related('question', 'selected_option').prefetch_related('question__options')
    
    correct_count = user_answers.filter(is_correct=True).count()
    skipped_count = user_answers.filter(selected_option__isnull=True).count()
    wrong_count = quiz.total_questions - correct_count - skipped_count
    
    # Recalculate score only if quiz was completed but score wasn't persisted
    # (safety net — normal flow always saves score in submit_answer)
    if quiz.completed_at and quiz.score == 0 and correct_count > 0 and quiz.total_questions > 0:
        calculated_score = round((correct_count / quiz.total_questions * 100))
        if calculated_score > 0:
            quiz.score = calculated_score
            quiz.save(update_fields=['score'])
    
    # Check if any explanations generated yet
    has_explanations = user_answers.exclude(error_explanation='').exists()
    
    # Calculate time statistics
    total_time = sum(a.time_taken for a in user_answers)
    avg_time = round(total_time / len(user_answers)) if user_answers else 0
    
    # Format total time using utility
    total_time_formatted = format_duration(total_time)

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
    2. Generates AI text for them in a batch (single AI call).
    3. Re-renders the answer list part of the page with explanations included.
    Uses the same AI model that was used to generate the quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    answers_needing_help = list(UserAnswer.objects.filter(
        quiz=quiz, 
        is_correct=False, 
        error_explanation=''
    ).select_related('question', 'selected_option').prefetch_related('question__options'))
    
    if answers_needing_help:
        model_to_use = quiz.model_used if quiz.model_used else None
        generator = QuizGenerator(model_name=model_to_use)
        
        qa_pairs = []
        for ans in answers_needing_help:
            correct_opt = next((o for o in ans.question.options.all() if o.is_correct), None)
            user_text = ans.selected_option.text if ans.selected_option else "Skipped"
            qa_pairs.append({
                'question': ans.question.text,
                'user_answer': user_text,
                'correct_answer': correct_opt.text if correct_opt else "Unknown"
            })
            
        explanations = generator.generate_batch_explanations(qa_pairs)
        
        # Bulk save
        for ans, explanation in zip(answers_needing_help, explanations):
            ans.error_explanation = str(explanation)
            
        UserAnswer.objects.bulk_update(answers_needing_help, ['error_explanation'])
    
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
    quiz.xp_awarded = False
    quiz.save(update_fields=['score', 'completed_at', 'xp_awarded'])
    
    return redirect('quiz_player', quiz_id=quiz.id)


@login_required
@require_http_methods(["POST"])
def delete_quiz(request, quiz_id):
    """
    Deletes a quiz and all associated data.
    Only the quiz owner can delete it.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    topic = quiz.topic_description[:50]
    quiz.delete()
    messages.success(request, f'Quiz "{topic}" deleted successfully.')
    return redirect('dashboard')
