from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    return render(request, 'core/home.html')


@require_GET
def languages_list(request):
    return render(request, 'core/languages.html')


def ratelimited_view(request, exception):
    """Custom handler for rate-limited requests."""
    return render(request, 'core/ratelimited.html', status=429)
