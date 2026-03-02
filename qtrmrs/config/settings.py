from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

load_dotenv(os.path.join(BASE_DIR.parent, '.env'))

# =============================================================================
# Core Settings
# =============================================================================

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-change-in-production'
    else:
        raise ValueError("SECRET_KEY environment variable is required in production")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =============================================================================
# Hosts Configuration
# =============================================================================

if DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
else:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# =============================================================================
# Application Definition
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local Apps
    'apps.core',
    'apps.users',
    'apps.quizzes',
    'apps.ai_agent',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add WhiteNoise for production static files
if not DEBUG:
    try:
        middleware_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1
        MIDDLEWARE.insert(middleware_idx, 'whitenoise.middleware.WhiteNoiseMiddleware')
    except ValueError:
        MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')
    
    # Add CSP middleware (after WhiteNoise)
    MIDDLEWARE.append('csp.middleware.CSPMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# Database
# =============================================================================

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,  # SSL required in production only
    )
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# Authentication
# =============================================================================

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# Password reset token validity (30 minutes)
PASSWORD_RESET_TIMEOUT = 1800

# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# =============================================================================
# Static & Media Files
# =============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Production storage configuration
if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }

# =============================================================================
# Email Configuration (Google SMTP)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'noreply@example.com')

# =============================================================================
# Security (Production Only)
# =============================================================================

if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Note: Setting CSRF_COOKIE_HTTPONLY = True may break HTMX CSRF functionality on cached pages.
    # Currently mitigated by server-side template tags, but there is a latent risk if templates 
    # relying heavily on HTMX are cached extensively without passing CSRF headers properly.
    CSRF_COOKIE_HTTPONLY = True
    
    # Other Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_BROWSER_XSS_FILTER = True
    
    # Content Security Policy
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = (
        "'self'", 
        "'unsafe-inline'",
        "https://unpkg.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
    )
    CSP_STYLE_SRC = (
        "'self'", 
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
    )
    CSP_FONT_SRC = (
        "'self'",
        "https://fonts.gstatic.com",
    )
    CSP_IMG_SRC = (
        "'self'",
        "data:",
        "https:",
    )

# =============================================================================
# Rate Limiting & AI Configuration
# =============================================================================

RATELIMIT_VIEW = 'apps.core.views.ratelimited_view'
DEFAULT_FALLBACK_MODEL = 'gemini-flash-lite-latest'
DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', DEFAULT_FALLBACK_MODEL)

# =============================================================================
# Logging
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps.ai_agent': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.quizzes': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
