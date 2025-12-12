# Development Plan & Architecture

This document outlines the architectural decisions, development phases, and future roadmap for **Quizzer AI**.

## 1. Architectural Philosophy

We moved away from a monolithic "spaghetti code" structure to a **Service-Oriented Django Architecture**.

- **Hybrid Logic:** Core business logic (quizzes, scoring) lives in `views.py` for simplicity and direct HTMX integration.
    
- **HTMX-First:** We avoid the complexity of a separate React frontend by using Django templates served via HTMX. This allows for SPA-like speed with SEO-friendly HTML.
    
- **AI-as-a-Service:** The AI integration is isolated in `apps/ai_agent/services.py`. The rest of the app doesn't know _how_ the quiz is generated, only that it receives JSON data.

- **Component-Based CSS:** Modular stylesheets (`theme.css`, `toast.css`, `skeleton.css`) for maintainability.

- **Test-Driven Quality:** pytest integration with fixtures for reliable testing.
    

## 2. Directory Structure

```
quizzer-ai/
├── qtrmrs/
│   ├── apps/                     # Modular Domains
│   │   ├── ai_agent/             # Gemini Client & Prompt Engineering
│   │   │   ├── services.py       # QuizGenerator with error handling & logging
│   │   │   ├── prompts.py        # AI prompt templates
│   │   │   └── client.py         # Gemini SDK wrapper
│   │   ├── core/                 # Landing pages & layout
│   │   ├── quizzes/              # Main Business Logic
│   │   │   ├── models.py         # Quiz, Question, Option, UserAnswer
│   │   │   ├── views.py          # HTMX views with study mode & timer
│   │   │   └── tests/            # Unit tests
│   │   └── users/                # Custom Auth & Profiles
│   ├── config/                   # Settings (Split into base/local/prod)
│   │   └── settings/
│   │       ├── base.py           # Logging config, AI settings
│   │       ├── local.py          # Dev settings
│   │       └── production.py     # Security headers
│   ├── static/
│   │   ├── css/
│   │   │   ├── theme.css         # Light/dark theme variables
│   │   │   ├── base.css          # Core + mobile + accessibility
│   │   │   ├── toast.css         # Toast notification styles
│   │   │   └── skeleton.css      # Loading skeleton animations
│   │   └── js/
│   │       └── toast.js          # Alpine.js toast store
│   ├── templates/                # HTML (organized by app)
│   │   └── quizzes/
│   │       └── partials/         # HTMX partials
│   │           ├── question_card.html
│   │           └── study_feedback.html
│   ├── logs/                     # Application logs
│   └── conftest.py               # Pytest fixtures
├── pyproject.toml                # Dependencies & pytest config
└── README.md
```

## 3. Development Phases (Completed)

### Phase 1: The Foundation ✅

- [x] Setup Django 5.x with `uv` package manager.
- [x] Refactor folder structure to `apps/` pattern.
- [x] Implement Modular Settings (`base.py`, `local.py`).
- [x] Create Custom User Model (`AbstractUser` with email login).


### Phase 2: The Data Layer ✅

- [x] Design Relational Schema: `Quiz` -> `Question` -> `Option` -> `UserAnswer`.
- [x] Implement `QuizAttempt` tracking for history.
- [x] Add `code_snippet` fields to support technical questions.
- [x] Add `time_taken` field to UserAnswer for timer tracking.
- [x] Add `is_study_mode` field to Quiz for study mode.


### Phase 3: The AI Service ✅

- [x] Integrate `google-generativeai` SDK.
- [x] Design `prompts.py` with strict JSON output enforcement.
- [x] Implement `QuizGenerator` service with error handling.
- [x] Add `AIError` class for granular error feedback (quota, auth, timeout).
- [x] Multiple model support (Flash, Flash Lite, Pro).
- [x] Performance logging with timing metrics.


### Phase 4: The Frontend System ✅

- [x] Build Base Template with HTMX & Alpine.js integration.
- [x] Design Theme System with CSS variables.
- [x] **Dark/Light Theme Toggle** with localStorage persistence.
- [x] Create responsive Grid layouts for Dashboard and Catalog.
- [x] **Toast Notification System** with Alpine.js store.
- [x] **Skeleton Loaders** with shimmer animations.


### Phase 5: The Interactive Player ✅

- [x] Build "Question Card" partials for HTMX swapping.
- [x] Implement "Split View" for coding questions (Code left, Options right).
- [x] Integrate Prism.js for syntax highlighting.
- [x] Create "Explain All Mistakes" logic for bulk AI analysis on results.
- [x] **Timer Per Question** with live display.
- [x] **Study Mode** with immediate feedback after each answer.


### Phase 6: The Chat Agent ✅

- [x] Build Natural Language Processing (NLP) prompt to extract intent.
- [x] Create Chat UI with "Thinking" states and suggestions.


### Phase 7: User Experience Polish ✅

- [x] **Smart Setup:** Auto-fill Language based on referer URL.
- [x] **Feedback:** Loading spinners on all buttons (HTMX indicators).
- [x] **Profile:** Avatar uploads and Settings management.


### Phase 8: Mobile & Accessibility ✅

- [x] **Mobile Optimization:** Responsive breakpoints at 768px/480px.
- [x] Touch-friendly targets (minimum 44px).
- [x] **Skip to Content** link for keyboard navigation.
- [x] **Focus-visible** outlines for accessibility.
- [x] `prefers-reduced-motion` support.
- [x] High contrast mode support.
- [x] Screen reader utilities (`.sr-only`).


### Phase 9: Code Quality ✅

- [x] **Structured Logging:** Console and file handlers with timing.
- [x] **Unit Tests:** pytest + pytest-django with fixtures.
- [x] Model tests for constraints and defaults.
- [x] View tests for authentication and functionality.
- [x] Input validation on all views.
- [x] HTTP method decorators for security.


## 4. Future Roadmap

### Short Term

- [ ] **Leaderboards:** Global ranking based on total score/quizzes taken.
- [ ] **Export:** Allow users to download their quiz results as PDF.
- [ ] **Daily Streaks:** Gamification to encourage daily practice.
- [ ] **Confetti Animation:** Celebrate perfect scores.
- [ ] **PWA Support:** Offline mode with service worker.

### Long Term

- [ ] **Multiplayer:** Real-time quiz battles using Django Channels (WebSockets).
- [ ] **Resume Analysis:** Upload a resume, generate questions based on listed skills.
- [ ] **Voice Mode:** Use Gemini's multimodal capabilities for oral technical interviews.
- [ ] **E2E Tests:** Playwright browser testing.
- [ ] **CI/CD Pipeline:** GitHub Actions for automated testing.


## 5. Testing

Run the test suite:

```bash
cd qtrmrs
uv run pytest -v
```

Run with coverage:

```bash
uv run pytest --cov=apps --cov-report=html
```

Current status: **15 tests passing**


## 6. Logging

Logs are written to console and `logs/quizzer.log`:

```
INFO 2025-12-12 10:50:00 [apps.ai_agent.services] Generating quiz: model=gemini-flash-latest...
INFO 2025-12-12 10:50:03 [apps.ai_agent.services] Quiz generated successfully: 5 questions in 3.24s
```

Configure log levels via environment:

```bash
DJANGO_LOG_LEVEL=DEBUG
```