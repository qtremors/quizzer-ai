# Quizzer AI Changelog

> **Project:** Quizzer AI  
> **Version:** 1.5.9  
> **Last Updated:** 2026-02-27

---

## [1.5.9] - 2026-02-27

### UI/UX (Frontend Overhaul)
- **UI-001:** Complete frontend overhaul to Google Material Design 3 (M3) principles using expressive custom CSS and HTMX.
- **UI-002:** Replaced existing styles with custom M3 CSS system for dynamic layouts, fluid typography (`Outfit`/`Roboto`), and core components.
- **UI-003:** Refactored core templates (home, dashboard, settings, authentication) to use M3 elevated cards, filled inputs, and dynamic grids.
- **UI-004:** Overhauled immersive quiz engine (setup, player, results) with interactive M3 option cards, dynamic progress bars, and semantic result coloring.
- **UI-005:** Redesigned AI Agent chat interface with quick suggestion chips, animated loading indicators, and modern pill-styled inputs.
- **UI-006:** Integrated premium M3 expressive micro-interactions, ripple effects, shimmer loads, and restyled snackbars/toasts for feedback.

---

## [1.5.8] - 2026-02-27

### Architecture
- **ARCH-002:** Split `quizzes/views.py` (616 lines) into `views/` package with `setup.py`, `player.py`, `results.py`, `demo.py`
- **ARCH-003:** Added `QuizQuerySet` custom manager with `for_user()` method on `Quiz` model
- **ARCH-004:** Extracted gamification logic from `submit_answer` into `award_quiz_completion()` in `quizzes/services.py`
- **ARCH-005:** Moved `AIModel` from `quizzes` app to `ai_agent` app using `SeparateDatabaseAndState` migrations (zero-downtime, no data migration)
- **ARCH-006:** Registered `UserProfile`, `Badge`, `UserBadge` in Django admin with list displays and filters

---

## [1.5.7] - 2026-02-26

### Performance
- **PERF-001:** Added `prefetch_related('question__options')` to `quiz_results` query to eliminate N+1 queries

### Changed
- **CODE-009:** Replaced hardcoded `'gemini-flash-lite-latest'` magic string with `settings.DEFAULT_AI_MODEL` across 4 files
- **CODE-011:** Consolidated `format_time` template filter to delegate to `format_duration()` from utils (now supports hours)
- **CODE-012:** Added singleton caching to `get_gemini_client()` — client is created once per process

---

## [1.5.6] - 2026-02-26

### Changed
- **ARCH-001:** Extracted duplicated quiz creation logic from `create_quiz`, `process_chat_message`, and `quick_quiz` into `quizzes/services.py` with `create_quiz_from_ai_data()`

### Added
- **TEST-001:** Mocked unit tests for all `QuizGenerator` methods (15 tests in `ai_agent/tests/test_services.py`)
- **TEST-002:** Integration tests for AI error handling and classification (16 tests in `ai_agent/tests/test_errors.py`)

---

## [1.5.5] - 2026-02-26

### Fixed
- **BUG-005:** `retry_quiz` now resets `xp_awarded` flag so users earn XP on retakes
- **BUG-006:** Fixed race condition in `submit_answer` — consolidated all quiz field updates onto `locked_quiz` inside the atomic block
- **BUG-007:** `quick_quiz` authenticated path now sets `quiz_type='tech'` and `language` fields
- **BUG-008:** `quick_quiz` authenticated path now saves `explanation` on questions
- **BUG-009:** `quiz_results` score recalculation guard tightened to avoid false triggers on legitimate 0% scores

---

## [1.5.4] - 2026-02-26

### Security
- **SEC-009:** Fixed email verification token parsing — URL now uses separate `<uidb64>/<token>/` path segments matching Django's own pattern, fixing always-failing `check_token()` due to hyphen splitting
- **SEC-010:** Added `@ratelimit(key='user', rate='3/h')` to `resend_verification` endpoint to prevent email flooding/DoS
- **SEC-011:** Added `@require_GET` decorator to `demo_results` view for HTTP method restriction consistency
- **SEC-012:** Fixed `check_models.py` `.env` path to resolve relative to script location instead of CWD

---

## [1.5.3] - 2026-01-24

### Added
- **Ratelimited Template:** New `templates/core/ratelimited.html` with proper styling

### Changed
- **Project Restructure:** Moved `pyproject.toml`, `uv.lock`, `requirements.txt` into `qtrmrs/` folder for cleaner root
- **UI Consistency:** Replaced all emojis with Material Symbols Outlined icons

### Fixed
- **BUG-001:** `ratelimited_view` now uses template instead of inline HTML
- **BUG-002:** `quick_quiz` level mismatch fixed (`'Easy'` → `'beginner'`)
- **BUG-003:** Added `@require_GET` and `@require_http_methods` decorators to demo views
- **BUG-004:** Fixed difficulty mismatch for logged-in users in `quick_quiz`

---

## [1.5.2] - 2026-01-24

### Added
- **Password Reset Flow:** Complete forgot password functionality with email-based recovery (30-min token expiry)
- **Email Verification:** Signup sends verification email; unverified users see warning banner with resend option
- **Google SMTP:** Gmail SMTP configured for production email delivery
- **CSP Enforcement:** Added `django-csp` middleware to enforce Content Security Policy headers in production

### Changed
- **Settings Consolidation:** Merged `base.py`, `local.py`, `production.py` into unified `settings.py` with DEBUG-based toggling
- **Timezone:** Changed from UTC to IST (Asia/Kolkata)

### Security
- **Session Size Limits:** Demo quiz session data now capped (max 10 questions, text truncation) to prevent DoS

---

## [1.5.1] - 2026-01-23

### Changed
- Migrated from `google-generativeai` to new `google-genai` SDK
- Updated `pyproject.toml` to disable package mode
- Standardized DB configuration using `dj-database-url`

### Added
- Management command `sync_models` to populate AI models on deployment
- Management command `set_active_models` to configure default AI models

---

## [1.5.0] - 2026-01-02

### Added
- Badge Display: Earned badges now shown on dashboard
- Quiz Deletion: Delete button with confirmation on dashboard
- Learning Interests UI: Added to settings page with edit form
- Dashboard Stats: Added Best Score and Correct Answers stats

### Changed
- Bulk Create: Options now use `bulk_create()` for fewer DB queries
- UserAnswer Ordering: Added `ordering = ['id']` to Meta class
- Import Cleanup: Consolidated all inline imports to top-level

### Fixed
- Quick Quiz Key Mismatch: Fixed `'question'` → `'text'` key inconsistency
- Demo Quiz Timer: Added Alpine.js timer to match main player UX
- XP Exploit: Added `xp_awarded` field to prevent retry farming
- Skip Confirmation: Added confirm dialog before skipping questions

---

## [1.3.0] - 2025-12-12

### Added
- Gamification System: XP, Leveling, Streaks, and 9 Achievement Badges
- Quick Quiz (Demo Mode): One-click guest access for random topic quizzes
- Confetti Animation: Celebration effect on 100% scores

### Technical
- New Models: `UserProfile`, `Badge`, `UserBadge`
- Service Layer: `apps/users/gamification.py` for logic

---

## [1.2.0] - 2025-12-12

### Fixed
- Type Comparison: Fixed option matching (int vs string) in quiz creation
- Theme Flash: Added inline script to prevent FOUC (Flash of Unstyled Content)
- Dropdown Hover: Theme-aware hover colors in navigation

### Changed
- CSS Refinement: Comprehensive viewport protection and wrapping for mobile
- Code Cleanup: Removed stale `is_study_mode` field

---

## [1.1.0] - 2025-12-12

### Added
- Theme Toggle: Dark/Light switcher with localStorage persistence
- Toast Notifications: Alpine.js based notification system
- Skeleton Loaders: Shimmer animations for loading states
- Timer Per Question: Live tracking and results analytics

### Accessibility
- Skip to Content link
- Focus-visible outlines
- Reduced Motion & High Contrast support

---

## [1.0.0] - 2025-11-19

### Added
- Service-Oriented Architecture: Modular `apps/` structure
- AI Integration: `QuizGenerator` service for Google Gemini API
- Intent Parsing: Natural Language Agent for chat-based quiz requests
- Immersive Player: Full-screen, HTMX-powered distraction-free UI
