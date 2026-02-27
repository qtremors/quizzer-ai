from django.db import transaction
from .models import Quiz, Question, Option


def create_quiz_from_ai_data(
    user,
    questions_data,
    *,
    quiz_type='tech',
    language='',
    topic_description='',
    difficulty='intermediate',
    ai_model=None,
    model_used=''
):
    """
    Create a Quiz with Questions and Options from AI-generated data.
    
    Consolidates the shared DB logic from create_quiz, process_chat_message,
    and quick_quiz into a single function.
    
    Args:
        user: The User creating the quiz.
        questions_data: List of question dicts from the AI generator.
        quiz_type: 'tech' or 'general'.
        language: Programming language or subject area.
        topic_description: Human-readable topic description.
        difficulty: 'beginner', 'intermediate', or 'expert'.
        ai_model: Optional AIModel instance for tracking.
        model_used: Model name string for tracking.
    
    Returns:
        The created Quiz instance.
    """
    with transaction.atomic():
        quiz = Quiz.objects.create(
            user=user,
            quiz_type=quiz_type,
            language=language,
            topic_description=topic_description[:255],
            difficulty=difficulty,
            total_questions=len(questions_data),
            ai_model=ai_model,
            model_used=model_used
        )

        options_to_create = []
        for q_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=q_data.get('text', '')[:2000],
                code_snippet=q_data.get('code_snippet') or '',
                explanation=q_data.get('explanation', '')
            )

            for opt in q_data.get('options', []):
                # Handle both string and dict options from AI
                if isinstance(opt, dict):
                    opt_text = str(opt.get('text', ''))[:255]
                else:
                    opt_text = str(opt)[:255]

                options_to_create.append(Option(
                    question=question,
                    text=opt_text,
                    is_correct=(opt_text == str(q_data.get('correct_answer', '')))
                ))

        if options_to_create:
            Option.objects.bulk_create(options_to_create)

    return quiz


def award_quiz_completion(quiz, user):
    """
    Handle all gamification logic when a quiz is completed.
    
    Awards XP, checks for level-ups, updates streaks, updates cached
    stats, and awards badges. Uses select_for_update to prevent race
    conditions on concurrent submissions.
    
    Args:
        quiz: The Quiz instance (must have score and completed_at set).
        user: The User who completed the quiz.
    
    Returns:
        Dict with keys: xp_earned, leveled_up, new_level, new_badges.
    """
    from apps.users.models import UserProfile
    from apps.users.gamification import (
        calculate_quiz_xp, calculate_level_from_xp,
        update_user_streak, check_and_award_badges
    )

    result = {
        'xp_earned': None,
        'leveled_up': False,
        'new_level': None,
        'new_badges': [],
    }

    correct_count = quiz.answers.filter(is_correct=True).count()

    with transaction.atomic():
        # Re-fetch quiz with lock to prevent concurrent XP awards
        locked_quiz = Quiz.objects.select_for_update().get(id=quiz.id)

        # Consolidate all field updates on the locked object
        locked_quiz.score = quiz.score
        locked_quiz.completed_at = quiz.completed_at

        if not locked_quiz.xp_awarded:
            # Get user profile with lock
            profile = UserProfile.objects.select_for_update().get(user=user)
            old_level = profile.level

            # Calculate and award XP
            total_time = sum(a.time_taken for a in quiz.answers.all())
            xp_earned = calculate_quiz_xp(correct_count, total_time, quiz.total_questions)
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
            if locked_quiz.score > profile.best_score:
                profile.best_score = locked_quiz.score

            profile.save()

            # Check and award badges
            new_badges = check_and_award_badges(user, profile)

            # Mark XP as awarded for this quiz
            locked_quiz.xp_awarded = True

            result['xp_earned'] = xp_earned
            result['leveled_up'] = leveled_up
            result['new_level'] = new_level if leveled_up else None
            result['new_badges'] = new_badges

        locked_quiz.save(update_fields=['score', 'completed_at', 'xp_awarded'])

    return result
