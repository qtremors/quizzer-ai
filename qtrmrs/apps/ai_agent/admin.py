from django.contrib import admin
from .models import AIModel


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'model_name', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
