from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Badge, UserBadge


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile', {'fields': ('is_student', 'avatar')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp', 'current_streak', 'best_score')
    list_filter = ('level',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('xp', 'level', 'current_streak', 'longest_streak', 'total_correct_answers', 'total_study_time', 'best_score')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'requirement_type', 'requirement_value')
    list_filter = ('requirement_type',)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge',)
    search_fields = ('user__email', 'user__username')


admin.site.register(User, CustomUserAdmin)