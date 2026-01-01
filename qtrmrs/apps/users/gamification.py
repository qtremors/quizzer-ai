"""
Gamification utilities for XP, levels, streaks, and badges.
"""
from datetime import timedelta
from django.utils import timezone


def calculate_quiz_xp(correct_count: int, total_time: int, total_questions: int) -> int:
    """
    Calculate XP earned from a quiz.
    
    XP Formula:
    - Base: 10 XP per correct answer
    - Time Bonus: 1 XP for every 5 seconds under 30s per question
      (e.g., answering in 10s = 4 bonus XP, answering in 25s = 1 bonus XP)
    - Perfect Bonus: +50 XP if 100% correct
    
    Args:
        correct_count: Number of correct answers
        total_time: Total time in seconds for all questions
        total_questions: Total number of questions
    
    Returns:
        Total XP earned
    """
    # Base XP: 10 per correct answer
    base_xp = correct_count * 10
    
    # Time bonus: for each correct answer, bonus based on speed
    # 30 seconds is "par", every 5 seconds faster = +1 XP
    time_bonus = 0
    if correct_count > 0 and total_questions > 0:
        avg_time = total_time / total_questions
        # Max 30s for bonus calculation
        if avg_time < 30:
            # Every 5 seconds under 30 = 1 bonus XP per correct answer
            bonus_per_answer = int((30 - avg_time) / 5)
            time_bonus = correct_count * bonus_per_answer
    
    # Perfect score bonus
    perfect_bonus = 50 if correct_count == total_questions and total_questions > 0 else 0
    
    return base_xp + time_bonus + perfect_bonus


def calculate_level_from_xp(total_xp: int) -> int:
    """
    Calculate level from total XP.
    Level thresholds: Level 1→2 = 100 XP, Level 2→3 = 200 XP, etc.
    
    Total XP for level N = sum(i * 100 for i in range(1, N))
    """
    level = 1
    xp_needed = 0
    while True:
        xp_for_next = level * 100
        if total_xp < xp_needed + xp_for_next:
            break
        xp_needed += xp_for_next
        level += 1
    return level


def update_user_streak(profile):
    """
    Update user's streak based on quiz completion.
    Call this after a quiz is completed.
    
    Args:
        profile: UserProfile instance
    
    Returns:
        Tuple of (new_streak, is_new_day)
    """
    today = timezone.now().date()
    is_new_day = profile.last_quiz_date != today
    
    if profile.last_quiz_date is None:
        # First quiz ever
        profile.current_streak = 1
    elif profile.last_quiz_date == today - timedelta(days=1):
        # Consecutive day - increment streak
        profile.current_streak += 1
    elif profile.last_quiz_date == today:
        # Same day - no change
        pass
    else:
        # Broke streak - reset to 1
        profile.current_streak = 1
    
    # Update longest streak
    profile.longest_streak = max(profile.longest_streak, profile.current_streak)
    profile.last_quiz_date = today
    
    return profile.current_streak, is_new_day


def check_and_award_badges(user, profile):
    """
    Check if user qualifies for any new badges and award them.
    
    Args:
        user: User instance
        profile: UserProfile instance
    
    Returns:
        List of newly awarded Badge instances
    """
    from .models import Badge, UserBadge
    
    awarded = []
    
    # Get all badges user doesn't have yet
    existing_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    available_badges = Badge.objects.exclude(id__in=existing_badge_ids)
    
    for badge in available_badges:
        earned = False
        
        if badge.requirement_type == 'level':
            earned = profile.level >= badge.requirement_value
        elif badge.requirement_type == 'streak':
            earned = profile.current_streak >= badge.requirement_value
        elif badge.requirement_type == 'score':
            earned = profile.best_score >= badge.requirement_value
        elif badge.requirement_type == 'correct':
            earned = profile.total_correct_answers >= badge.requirement_value
        
        if earned:
            UserBadge.objects.create(user=user, badge=badge)
            awarded.append(badge)
    
    return awarded
