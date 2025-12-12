from django.contrib import admin
from .models import AIModel, Quiz, Question, Option, UserAnswer


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('id', 'quiz', 'text_preview')
    list_filter = ('quiz__language',)
    search_fields = ('text',)
    
    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'Question'


class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    readonly_fields = ('question', 'selected_option', 'is_correct')
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'language', 'topic_description', 'user', 'difficulty', 'score', 'created_at', 'completed_at')
    list_filter = ('difficulty', 'quiz_type', 'language', 'created_at')
    search_fields = ('topic_description', 'user__email', 'language')
    inlines = [UserAnswerInline]
    date_hierarchy = 'created_at'


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'model_name', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')


admin.site.register(Question, QuestionAdmin)
admin.site.register(UserAnswer)
