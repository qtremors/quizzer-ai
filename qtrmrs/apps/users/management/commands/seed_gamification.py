"""
Management command to seed initial badge definitions and create profiles for existing users.
"""
from django.core.management.base import BaseCommand
from apps.users.models import User, UserProfile, Badge


BADGE_DEFINITIONS = [
    # Level badges
    {'name': 'Level 5', 'icon': '💪', 'description': 'Reached Level 5', 'requirement_type': 'level', 'requirement_value': 5},
    {'name': 'Level 10', 'icon': '🧠', 'description': 'Reached Level 10', 'requirement_type': 'level', 'requirement_value': 10},
    {'name': 'Level 25', 'icon': '🚀', 'description': 'Reached Level 25', 'requirement_type': 'level', 'requirement_value': 25},
    {'name': 'Level 50', 'icon': '👑', 'description': 'Reached Level 50', 'requirement_type': 'level', 'requirement_value': 50},
    
    # Streak badges
    {'name': 'Week Warrior', 'icon': '🔥', 'description': '7-day streak', 'requirement_type': 'streak', 'requirement_value': 7},
    {'name': 'Month Master', 'icon': '🏆', 'description': '30-day streak', 'requirement_type': 'streak', 'requirement_value': 30},
    
    # Score badges
    {'name': 'Perfectionist', 'icon': '⭐', 'description': 'Scored 100% on a quiz', 'requirement_type': 'score', 'requirement_value': 100},
    
    # Correct answers badges
    {'name': 'Century Club', 'icon': '💯', 'description': 'Answered 100 questions correctly', 'requirement_type': 'correct', 'requirement_value': 100},
    {'name': 'Knowledge Master', 'icon': '📚', 'description': 'Answered 500 questions correctly', 'requirement_type': 'correct', 'requirement_value': 500},
]


class Command(BaseCommand):
    help = 'Seeds badge definitions and creates profiles for existing users'

    def handle(self, *args, **options):
        # Create badges
        badges_created = 0
        for badge_data in BADGE_DEFINITIONS:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                badges_created += 1
                self.stdout.write(f"  Created badge: {badge}")
        
        self.stdout.write(self.style.SUCCESS(f'Badges: {badges_created} created, {len(BADGE_DEFINITIONS) - badges_created} already existed'))
        
        # Create profiles for existing users who don't have one
        profiles_created = 0
        users_without_profile = User.objects.filter(profile__isnull=True)
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            profiles_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'User profiles: {profiles_created} created'))
