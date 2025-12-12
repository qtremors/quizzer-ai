from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
    """
    Extends the standard Django Signup form but uses our Custom User model.
    It automatically handles password confirmation and hashing.
    """
    class Meta:
        model = User
        # Only ask for Email and Username (display name)
        fields = ('email', 'username') 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add styling classes to match theme
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class LoginForm(AuthenticationForm):
    """
    Standard login form with custom styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username']  # email removed: requires verification flow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})