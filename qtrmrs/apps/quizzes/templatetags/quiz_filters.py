from django import template

register = template.Library()


@register.filter
def format_time(seconds):
    """Format seconds into human-readable time string"""
    if seconds is None or seconds == 0:
        return "0s"
    
    seconds = int(seconds)
    if seconds >= 60:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    return f"{seconds}s"


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
