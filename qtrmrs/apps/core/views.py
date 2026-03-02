from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import JsonResponse


@require_GET
def home(request):
    return render(request, 'core/home.html')


@require_GET
def languages_list(request):
    return render(request, 'core/languages.html')


def ratelimited_view(request, exception):
    """Custom handler for rate-limited requests."""
    return render(request, 'core/ratelimited.html', status=429)


@require_GET
def health_check(request):
    """Basic health check for monitoring and load balancers."""
    from django.db import connection
    try:
        connection.ensure_connection()
        return JsonResponse({'status': 'ok'}, status=200)
    except Exception:
        return JsonResponse({'status': 'error', 'detail': 'database unavailable'}, status=503)
