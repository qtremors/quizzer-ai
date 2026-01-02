from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import SignUpForm, LoginForm, UserUpdateForm 
from apps.quizzes.models import Quiz


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login after signup
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'users/signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Safe redirect - validate 'next' parameter to prevent open redirect
            next_url = request.POST.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@require_GET
def user_dashboard(request):
    """
    Shows quiz history and statistics with pagination.
    """
    user_quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination - 12 quizzes per page
    paginator = Paginator(user_quizzes, 12)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1
    quizzes_page = paginator.get_page(page_number)
    
    # Calculate Stats (on all quizzes, not just this page)
    total_quizzes = user_quizzes.count()
    avg_score = user_quizzes.aggregate(Avg('score'))['score__avg'] or 0
    
    # Count incomplete quizzes (no completed_at)
    incomplete_count = user_quizzes.filter(completed_at__isnull=True).count()
    
    context = {
        'quizzes': quizzes_page,
        'total_quizzes': total_quizzes,
        'avg_score': round(avg_score, 1),
        'incomplete_count': incomplete_count,
        'page_obj': quizzes_page,  # For pagination template
        'profile': request.user.profile,  # For level/XP/streak display
        'badges': request.user.earned_badges.select_related('badge').order_by('-earned_at')[:6],  # Recent badges
    }
    return render(request, 'users/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def account_settings(request):
    # Initialize forms with current user instance
    profile_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    profile = request.user.profile

    if request.method == 'POST':
        
        if 'update_profile' in request.POST:
            profile_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('account_settings')
            else:
                messages.error(request, 'Error updating profile.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                login(request, user) # Keep user logged in
                messages.success(request, 'Password changed successfully!')
                return redirect('account_settings')
            else:
                messages.error(request, 'Error changing password.')
        
        elif 'update_interests' in request.POST:
            interests = request.POST.get('learning_interests', '')
            profile.learning_interests = interests
            profile.save(update_fields=['learning_interests'])
            messages.success(request, 'Learning interests updated!')
            return redirect('account_settings')

    # Apply styles
    for field in password_form.fields.values():
        field.widget.attrs.update({'class': 'form-input'})

    return render(request, 'users/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile,
    })
