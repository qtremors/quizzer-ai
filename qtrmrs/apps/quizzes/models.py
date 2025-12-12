from django.db import models
from django.conf import settings


class AIModel(models.Model):
    """Manages available Gemini versions (Flash, Pro, etc.)"""
    display_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, help_text="The API string, e.g., 'gemini-1.5-flash'")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        # Ensure only one default model exists
        if self.is_default:
            AIModel.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"


class Quiz(models.Model):
    """Represents a generated quiz session"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    ]
    
    QUIZ_TYPE_CHOICES = [
        ('tech', 'Programming/Technology'),
        ('general', 'General Knowledge'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='tech')
    language = models.CharField(max_length=50, help_text="Language/subject for the quiz")
    topic_description = models.CharField(max_length=255, help_text="The topic user asked for")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    model_used = models.CharField(max_length=100, blank=True)  # Fallback string for display
    total_questions = models.IntegerField(default=0)
    score = models.IntegerField(default=0, help_text="Score percentage")
    completed_at = models.DateTimeField(null=True, blank=True)
    


    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['quiz_type']),
        ]
        ordering = ['-created_at']
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return f"{self.language} ({self.difficulty}) - {self.user.email}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    # Stores the code block (optional)
    code_snippet = models.TextField(blank=True, null=True, help_text="Code context for the question")
    explanation = models.TextField(blank=True, help_text="AI explanation for the correct answer")
    
    class Meta:
        indexes = [
            models.Index(fields=['quiz']),
        ]
    
    def __str__(self):
        return self.text[:50]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['question', 'is_correct']),
        ]

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    """Tracks which option the user selected"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    
    # Time tracking
    time_taken = models.PositiveIntegerField(default=0, help_text="Time taken in seconds")
    
    # Store the specific AI explanation for *this* error here if needed
    error_explanation = models.TextField(blank=True)
    
    class Meta:
        # Prevent duplicate answers for the same question
        unique_together = [['quiz', 'question']]
        indexes = [
            models.Index(fields=['quiz', 'is_correct']),
        ]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} Q{self.question_id} - {self.quiz.topic_description[:20]}"
