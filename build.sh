#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install Dependencies
pip install -r requirements.txt

# 2. Move into the project folder
cd qtrmrs

# 3. Set production settings for collectstatic
export DJANGO_SETTINGS_MODULE=config.settings.production

# 4. Collect Static Files
python manage.py collectstatic --no-input

# 4. Apply Migrations
python manage.py migrate

# 5. Auto-Create Superuser (The Fix)
# This reads the Env Vars you just set.
# The "|| true" ensures the build doesn't fail if the user already exists.
python manage.py createsuperuser --noinput || true