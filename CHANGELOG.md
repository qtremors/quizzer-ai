# Quizzer AI Changelog

> **Project:** Quizzer AI  
> **Version:** 1.5.4  
> **Last Updated:** 2026-02-26

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
