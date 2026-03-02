from django import template
from apps.quizzes.utils import format_duration

register = template.Library()


@register.filter
def format_time(seconds):
    """Format seconds into human-readable time string."""
    if seconds is None:
        return "0s"
    try:
        return format_duration(int(seconds))
    except (TypeError, ValueError):
        return "0s"


@register.filter
def div(value, arg):
    """Integer division"""
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def mod(value, arg):
    """Modulo operation"""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0
