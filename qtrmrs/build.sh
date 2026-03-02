#!/usr/bin/env bash
# Render Build Script for Quizzer AI
# exit on error
set -o errexit

# 1. (Already in project root)

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Set production settings
export DJANGO_SETTINGS_MODULE=config.settings

# 4. Collect Static Files
python manage.py collectstatic --no-input

# 5. Apply Migrations
python manage.py migrate

# 5.5. Seed gamification data (badges) and AI model config
python manage.py seed_gamification
python manage.py set_active_models

# 6. Create Superuser (only if it doesn't exist)
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
if email and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=email,
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    )
    print(f'Superuser {email} created.')
else:
    print('Superuser already exists or email not set, skipping.')
"