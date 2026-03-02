from django.db import models, transaction


class AIModel(models.Model):
    """Manages available Gemini versions (Flash, Pro, etc.)"""
    display_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, help_text="The API string, e.g., 'gemini-1.5-flash'")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        # PR-002: Atomic transaction with select_for_update to prevent race conditions
        with transaction.atomic():
            if self.is_default:
                AIModel.objects.select_for_update().filter(
                    is_default=True
                ).exclude(pk=self.pk).update(is_default=False)
            super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        db_table = 'quizzes_aimodel'
        constraints = [
            models.UniqueConstraint(
                fields=['is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_ai_model',
            ),
        ]
