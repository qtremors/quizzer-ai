"""
Tests for users app - authentication, profile, gamification.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile, Badge, UserBadge
from apps.users.gamification import calculate_quiz_xp, calculate_level_from_xp, update_user_streak

User = get_user_model()


class TestAuthentication:
    """Tests for authentication views."""
    
    def test_signup_page_loads(self, client, db):
        """Test signup page is accessible."""
        response = client.get(reverse('signup'))
        assert response.status_code == 200
        assert b'Sign Up' in response.content
    
    def test_login_page_loads(self, client, db):
        """Test login page is accessible."""
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert b'Log In' in response.content
    
    def test_signup_creates_user_and_profile(self, client, db):
        """Test that signup creates user with profile."""
        response = client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        # Should redirect after successful signup
        assert response.status_code == 302
        
        # User and profile should exist
        user = User.objects.get(email='new@example.com')
        assert user.username == 'newuser'
        assert hasattr(user, 'profile')
        assert user.profile.level == 1
        assert user.profile.xp == 0


class TestDashboard:
    """Tests for dashboard view."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_dashboard_shows_stats(self, authenticated_client, quiz, db):
        """Test dashboard displays user statistics."""
        response = authenticated_client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert b'Dashboard' in response.content
        # Should show stats section
        assert b'Level' in response.content
        assert b'Streak' in response.content


class TestSettings:
    """Tests for account settings."""
    
    def test_settings_requires_login(self, client):
        """Test settings page requires authentication."""
        response = client.get(reverse('account_settings'))
        assert response.status_code == 302
    
    def test_settings_page_loads(self, authenticated_client, db):
        """Test settings page loads."""
        response = authenticated_client.get(reverse('account_settings'))
        assert response.status_code == 200
        assert b'Account Settings' in response.content
    
    def test_update_learning_interests(self, authenticated_client, user, db):
        """Test updating learning interests."""
        response = authenticated_client.post(reverse('account_settings'), {
            'update_interests': True,
            'learning_interests': 'Python, JavaScript, React',
        })
        assert response.status_code == 302
        
        # Refresh from database
        user.refresh_from_db()
        assert user.profile.learning_interests == 'Python, JavaScript, React'


class TestGamification:
    """Tests for gamification utilities."""
    
    def test_calculate_xp_correct_answers(self):
        """Test XP calculation for correct answers."""
        # 3 correct, 60 seconds total, 5 questions
        xp = calculate_quiz_xp(3, 60, 5)
        assert xp >= 30  # 10 XP per correct answer minimum
    
    def test_calculate_xp_perfect_score_bonus(self):
        """Test bonus XP for perfect score."""
        # Perfect score (5/5, 50 seconds total, 5 questions)
        xp = calculate_quiz_xp(5, 50, 5)
        # 50 base + 50 bonus + time bonus
        assert xp >= 100
    
    def test_calculate_level_from_xp(self):
        """Test level calculation."""
        assert calculate_level_from_xp(0) == 1
        assert calculate_level_from_xp(99) == 1
        assert calculate_level_from_xp(100) == 2
        assert calculate_level_from_xp(300) == 3  # 100 + 200 = 300 for level 3
    
    def test_streak_update(self, user, db):
        """Test streak tracking."""
        from datetime import date
        profile = user.profile
        
        # First quiz today should start streak
        update_user_streak(profile)
        assert profile.current_streak >= 1


class TestBadges:
    """Tests for badge system."""
    
    @pytest.fixture
    def badges(self, db):
        """Create test badges."""
        Badge.objects.create(
            name='Level 5',
            icon='⭐',
            description='Reach level 5',
            requirement_type='level',
            requirement_value=5
        )
        Badge.objects.create(
            name='First Quiz',
            icon='🎯',
            description='Complete your first quiz',
            requirement_type='quizzes',
            requirement_value=1
        )
        return Badge.objects.all()
    
    def test_badge_not_awarded_below_requirement(self, user, badges, db):
        """Test badge not given if requirement not met."""
        from apps.users.gamification import check_and_award_badges
        
        # User is level 1, shouldn't get Level 5 badge
        user.profile.level = 1
        user.profile.save()
        
        check_and_award_badges(user, user.profile)
        
        level_badge = Badge.objects.get(name='Level 5')
        assert not UserBadge.objects.filter(user=user, badge=level_badge).exists()
