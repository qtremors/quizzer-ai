from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """Extended profile for gamification and preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # === XP & Leveling ===
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    
    # === Streak Tracking ===
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_quiz_date = models.DateField(null=True, blank=True)
    
    # === Quiz Preferences ===
    preferred_difficulty = models.CharField(max_length=20, default='Intermediate')
    preferred_num_questions = models.PositiveIntegerField(default=5)
    include_code_snippets = models.BooleanField(default=False)
    
    # === Learning Interests (comma-separated) ===
    learning_interests = models.TextField(blank=True, default='')
    
    # === Personalization Settings ===
    show_recommendations = models.BooleanField(default=True)
    
    # === Cached Stats ===
    total_correct_answers = models.PositiveIntegerField(default=0)
    total_study_time = models.PositiveIntegerField(default=0)  # Seconds
    best_score = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Profile: {self.user.email} (Level {self.level})"
    
    def get_learning_interests_list(self):
        """Returns list of learning interests."""
        if not self.learning_interests:
            return []
        return [x.strip() for x in self.learning_interests.split(',') if x.strip()]
    
    def set_learning_interests_list(self, interests):
        """Sets learning interests from a list."""
        self.learning_interests = ','.join(interests)
    
    @property
    def xp_for_next_level(self):
        """XP required to reach next level (scales with level)."""
        return self.level * 100
    
    @property
    def current_level_xp(self):
        """XP accumulated before current level."""
        return sum((i * 100) for i in range(1, self.level))
    
    @property
    def xp_in_current_level(self):
        """XP earned within current level."""
        return self.xp - self.current_level_xp
    
    @property
    def xp_progress_percent(self):
        """Progress to next level as percentage."""
        if self.xp_for_next_level == 0:
            return 100
        return min(100, int((self.xp_in_current_level / self.xp_for_next_level) * 100))


class Badge(models.Model):
    """Predefined achievement badges."""
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10)  # Emoji
    description = models.CharField(max_length=200)
    requirement_type = models.CharField(max_length=20)  # 'level', 'streak', 'score', 'quizzes'
    requirement_value = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """Badges earned by users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
    
    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


# === Signals ===

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)