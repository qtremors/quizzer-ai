from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    return render(request, 'core/home.html')


@require_GET
def languages_list(request):
    return render(request, 'core/languages.html')


def ratelimited_view(request, exception):
    """Custom handler for rate-limited requests."""
    return HttpResponse(
        '''
        <div style="text-align: center; padding: 40px; background: rgba(239,68,68,0.1); 
                    border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; margin: 20px;">
            <h3 style="color: #ef4444; margin-bottom: 8px;">⏱️ Too Many Requests</h3>
            <p style="color: #888;">Please wait a moment before generating another quiz.</p>
        </div>
        ''',
        status=429
    )
