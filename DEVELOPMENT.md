# Quizzer AI - Developer Documentation

> Comprehensive documentation for developers working on Quizzer AI.

**Version:** 1.6.0 | **Last Updated:** 2026-03-02

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [AI Workflow](#ai-workflow)
- [Environment Variables](#environment-variables)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Architecture Overview

Quizzer AI follows a **Service-Oriented Django** architecture:

```
┌──────────────────────────────────────────────────────────────┐
│                        UI (HTML + HTMX)                      │
│        Interactive Player & Dashboard using Alpine.js        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Django Apps (Business Logic)              │
│         Modular Apps for Quizzes, Users, and Core            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    AI Service (Gemini API)                   │
│         Quiz Generation, Intent Parsing & Explanations       │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **HTMX-First** | Avoids the complexity of a separate React/Vue frontend while maintaining SPA-like speed. |
| **Service Isolation** | AI integration is isolated in `apps/ai_agent/services.py` for decoupled logic. |
| **Custom User Model** | Uses `AbstractUser` with email as the primary identifier for modern auth flow. |
| **Hybrid Logic** | Core business logic lives in views for simplicity and direct HTMX integration. |

---

## Project Structure

```
quizzer-ai/
├── qtrmrs/
│   ├── apps/                     # Modular Domains
│   │   ├── ai_agent/             # Gemini Client & Prompt Engineering
│   │   ├── core/                 # Landing pages & layout
│   │   ├── quizzes/              # Main Business Logic
│   │   └── users/                # Custom Auth & Profiles
│   ├── config/                   # Settings & URL config
│   ├── static/                   # CSS/JS/Images
│   ├── templates/                # HTML (organized by app)
│   ├── conftest.py               # Pytest fixtures
│   └── pyproject.toml            # Dependencies & pytest config
├── DEVELOPMENT.md                # This file
├── CHANGELOG.md                  # Version history
├── LICENSE.md                    # License terms
└── README.md
```

---

## Database Schema

### Models Overview (9 total)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| **User** | Custom authentication | `email`, `username`, `is_student` |
| **UserProfile** | Gamification & stats | `xp`, `level`, `current_streak`, `interests` |
| **Quiz** | Quiz session data | `quiz_type`, `topic_description`, `score`, `ai_model` |
| **Question** | Generated questions | `text`, `code_snippet`, `explanation` |
| **Option** | Multiple choice options | `text`, `is_correct` |
| **UserAnswer** | User responses | `selected_option`, `is_correct`, `time_taken` |
| **AIModel** | Gemini model versions | `model_name`, `is_active`, `is_default` |
| **Badge** | Achievement definitions | `name`, `icon`, `requirement_type` |
| **UserBadge** | Earned achievements | `user`, `badge`, `earned_at` |

### Relationships

- `User` ──── 1:1 ──── `UserProfile`
- `User` ──── 1:N ──── `Quiz` ──── 1:N ──── `Question` ──── 1:N ──── `Option`
- `Quiz` ──── 1:N ──── `UserAnswer` ──── N:1 ──── `Question`

---

## AI Workflow

The system uses a 3-step AI pipeline optimized for speed and accuracy:

1.  **Intent Parsing**: Natural language requests (e.g., "Python quiz") are converted into structured parameters (Subject, Topic, Difficulty).
2.  **Quiz Generation**: Uses strict JSON enforcement in prompts to generate questions, options, and explanations in a single pass.
3.  **Mistake Explanation**: When requested, the AI analyzes aggregate mistakes to provide a cohesive learning summary.

---

## AI Model Management

The project includes several tools to manage the connection with Google's Gemini API:

### 1. Verify Connectivity
Run this script to check if your API key is valid and see which models are available from Google:
```bash
uv run check_models.py
```

### 2. Sync Models to Database
Populates the `AIModel` table with all available models from the API:
```bash
uv run python qtrmrs/manage.py sync_models
```

### 3. Configure Active Models
Sets specific models as active and configures the default model (e.g., `gemini-flash-lite-latest`):
```bash
uv run python qtrmrs/manage.py set_active_models
```

---

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key from Google AI Studio | `AIzaSy...` |
| `DATABASE_URL` | NeonDB/PostgreSQL Connection String | `postgres://user:pass@host/db` |
| `SECRET_KEY` | Django secret key for production | `django-insecure...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enables debug mode | `False` |
| `DJANGO_LOG_LEVEL` | Log verbosity (INFO, DEBUG, ERROR) | `INFO` |
| `DEFAULT_AI_MODEL` | Gemini model version | `gemini-flash-lite-latest` |

---

## Configuration

### Settings Modules

- `config/settings.py`: Unified settings with DEBUG-based toggling for dev/production.

---

## Testing

### Running Tests

```bash
# All tests
cd qtrmrs
uv run pytest -v

# With coverage
uv run pytest --cov=apps --cov-report=html
```

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in environment.
- [ ] Configure `ALLOWED_HOSTS`.
- [ ] Run `python manage.py collectstatic`.
- [ ] Set up PostgreSQL via `DATABASE_URL`.
- [ ] Configure `SECURE_SSL_REDIRECT` in `settings.py`.

---

<p align="center">
  <a href="README.md">← Back to README</a>
</p>
