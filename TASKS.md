# Quizzer AI - Tasks

> **Project:** Quizzer AI  
> **Version:** 1.5.4  
> **Last Updated:** 2026-02-26  

---

## 🔴 Critical Priority

### Security
- [x] **SEC-009:** Email verification token parsing uses fragile `rsplit('-', 1)`
  - `verify_email` in `users/views.py` splits the URL token with `rsplit('-', 1)` to separate `uid` from `token`
  - Django's token generator produces tokens containing hyphens (e.g., `cbnh7q-abc123...`), so `rsplit('-', 1)` only splits the *last* hyphen
  - This means the `uid` portion absorbs part of the token, so `check_token()` will always fail
  - URL pattern `<str:token>` also captures the `uid-token` as a single string, unlike Django's built-in pattern that uses separate `<uidb64>` and `<token>` path segments
  - **Impact:** Email verification silently never works; users always see "Invalid or expired verification link"
  - **Fix:** Use separate URL path segments like `verify-email/<uidb64>/<token>/` matching Django's own pattern
  - **Effort:** 30 minutes

- [x] **SEC-010:** No rate limiting on `resend_verification` endpoint
  - Attackers can abuse this to send unlimited verification emails, causing email flooding/DoS
  - Add `@ratelimit(key='user', rate='3/h')` decorator
  - **Effort:** 10 minutes

- [x] **SEC-011:** `demo_results` view missing HTTP method restriction
  - `demo_results` in `quizzes/views.py` (line 627) accepts any HTTP method including POST/PUT/DELETE
  - All other views properly use `@require_GET` or `@require_http_methods`
  - Add `@require_GET` decorator for consistency
  - **Effort:** 5 minutes

- [x] **SEC-012:** `check_models.py` loads `.env` from wrong directory
  - Calls `load_dotenv()` with no path, which only checks the current directory
  - The `.env` file lives at the project root (`quizzer-ai/.env`), but `check_models.py` is in `qtrmrs/`
  - If run as `uv run check_models.py` from `qtrmrs/`, it won't find the API key
  - **Fix:** Use `load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))`
  - **Effort:** 5 minutes

### Bugs
- [ ] **BUG-005:** `retry_quiz` does not reset `xp_awarded` flag
  - `retry_quiz` in `quizzes/views.py` (line 404) resets `score` and `completed_at` but leaves `xp_awarded = True`
  - On retry completion, the user will never earn XP again since the flag is still `True`
  - Add `quiz.xp_awarded = False` and include it in `save(update_fields=[...])`
  - **Effort:** 5 minutes

- [ ] **BUG-006:** Race condition between `quiz.save()` and `locked_quiz.save()` in `submit_answer`
  - In `submit_answer`, `quiz.score` and `quiz.completed_at` are set on the original `quiz` object (line 232-233)
  - Then inside the `transaction.atomic()` block, a re-fetched `locked_quiz` saves `xp_awarded` (line 279)
  - After the block, `quiz.save(update_fields=['score', 'completed_at'])` (line 282) writes the *original* `quiz` object
  - Since `locked_quiz` and `quiz` are different Python objects, this creates a potential overwrite if concurrent requests modify the same row
  - **Fix:** Consolidate all quiz field updates onto a single object
  - **Effort:** 30 minutes

- [ ] **BUG-007:** `quick_quiz` for authenticated users doesn't set `quiz_type` field
  - The `Quiz.objects.create(...)` call at line 501 doesn't pass `quiz_type`, so it defaults to `'tech'`
  - But the original quiz setup path in `create_quiz` explicitly sets `quiz_type='tech'`; quick quiz should too
  - Additionally, `language` field is not set — it defaults to `''` instead of the chosen language
  - **Fix:** Add `quiz_type='tech'` and `language=language` to the create call
  - **Effort:** 5 minutes

- [ ] **BUG-008:** `quick_quiz` authenticated path doesn't save `explanation` on questions
  - `create_quiz` and `process_chat_message` both save `explanation=q_data.get('explanation', '')` on each question
  - `quick_quiz`'s authenticated path (line 511-515) does not, causing explanations to be lost
  - **Effort:** 5 minutes

- [ ] **BUG-009:** `quiz_results` score recalculation can trigger on legitimate 0% scores
  - Line 316: `if quiz.score == 0 and correct_count > 0` recalculates the score
  - But if the quiz was already scored correctly as 0% (all wrong), and the user revisits results, it stays 0 — this is fine
  - However, the real issue is that `quiz.score` is stored as an integer (0-100) but could be legitimately 0 while `completed_at` is set, so the condition is subtly wrong for edge cases where a quiz completes with some correct answers but due to rounding ends at 0%
  - **Effort:** 15 minutes

---

## 🟠 High Priority (This Sprint)

### Testing
- [ ] **TEST-001:** No tests for `ai_agent` module
  - `apps/ai_agent/tests.py` is empty placeholder
  - Add mocked tests for `QuizGenerator` class
  - **Effort:** 4-6 hours

- [ ] **TEST-002:** No integration tests for AI service with mocked responses
  - Need tests for error handling (quota, timeout, 404, validation)
  - **Effort:** 2-3 hours

### Architecture
- [ ] **ARCH-001:** Quiz creation logic duplicated across 3 views
  - `create_quiz`, `process_chat_message`, `quick_quiz` share ~100 lines each
  - Extract to `apps/quizzes/services.py` with `create_quiz_from_ai()` function
  - **Effort:** 2-3 hours

### Performance
- [ ] **PERF-001:** N+1 query in `quiz_results` view
  - Missing `.prefetch_related('question__options')` on line 309
  - **Effort:** 15 minutes

### Code Quality
- [ ] **CODE-009:** Magic string `'gemini-flash-lite-latest'` repeated in 4 files
  - Define `DEFAULT_FALLBACK_MODEL` constant in settings
  - Reference from: ai_agent/views.py, quizzes/views.py (×2)
  - **Effort:** 30 minutes

- [x] ~~**CODE-010:** Settings.py line 150 has typo in DEFAULT_AI_MODEL default~~
  - **FALSE:** Verified `settings.py` line 237 has the correct value `'gemini-flash-lite-latest'`. No typo exists.

- [ ] **CODE-011:** `format_duration()` in `quizzes/utils.py` duplicates `format_time` template filter
  - `quiz_filters.py` has a `format_time` filter that does the same thing as `format_duration()` in `utils.py`
  - `format_duration` handles hours, `format_time` doesn't — inconsistent behavior
  - Consolidate into one function and use it everywhere
  - **Effort:** 20 minutes

- [ ] **CODE-012:** Gemini client created on every `QuizGenerator` instantiation
  - `get_gemini_client()` creates a new `genai.Client()` on every call — no caching or singleton
  - Each quiz generation, intent parsing, and explanation request creates a fresh client
  - Add module-level caching or a singleton pattern
  - **Effort:** 15 minutes

---

## ⚠️ Medium Priority (Next Sprint)

### Architecture
- [ ] **ARCH-002:** View files too large - `quizzes/views.py` is 652 lines
  - Split into: `setup.py`, `player.py`, `results.py`, `demo.py`
  - **Effort:** 2-4 hours

- [ ] **ARCH-003:** Missing model managers
  - `Quiz.objects.filter(user=request.user).order_by('-created_at')` repeated 4 times
  - Create `QuizQuerySet` with `for_user()` method
  - **Effort:** 1 hour

- [ ] **ARCH-004:** Gamification coupling in `submit_answer`
  - Profile updates tightly coupled (lines 241-288)
  - Consider Django signals or separate service for XP/badge logic
  - **Effort:** 2-3 hours

- [ ] **ARCH-005:** `AIModel` model lives in `quizzes` app but logically belongs in `ai_agent`
  - `AIModel` is defined in `apps/quizzes/models.py` but is conceptually an AI concern
  - Both `ai_agent` views and management commands import it from `quizzes`
  - Consider moving to `ai_agent/models.py` (currently empty)
  - **Effort:** 1-2 hours (requires migration)

- [ ] **ARCH-006:** `Badge` and `UserBadge` admin registrations missing
  - `users/admin.py` only registers `User` — `UserProfile`, `Badge`, and `UserBadge` are not registered
  - Admins cannot manage badges or view user profiles in the admin panel
  - **Effort:** 15 minutes

### Security
- [ ] **SEC-006:** `'unsafe-inline'` in CSP script-src
  - Weakens XSS protection but required for HTMX/Alpine.js inline code
  - Consider nonces in future for tighter security
  - **Effort:** 4-6 hours (significant refactor)

- [ ] **SEC-008:** No rate limiting on password reset endpoint
  - Add `@ratelimit(key='ip', rate='5/h')` to prevent enumeration
  - **Effort:** 30 minutes

- [ ] **SEC-013:** `CSRF_COOKIE_HTTPONLY = True` may break HTMX CSRF token injection
  - In production, `CSRF_COOKIE_HTTPONLY = True` prevents JavaScript from reading the CSRF cookie
  - `base.html` line 208 injects the CSRF token via `{{ csrf_token }}` template tag (server-side), so it works
  - However, if any HTMX request occurs on a page not rendered by Django (e.g., cached), the token may be stale
  - This is a latent risk rather than an active bug; document the dependency
  - **Effort:** 30 minutes (documentation/testing)

- [ ] **SEC-014:** `signup_view` doesn't sanitize or validate `username` for XSS
  - The `username` is rendered unescaped in the navbar dropdown (`{{ user.username }}`)
  - Django templates auto-escape by default, so this is mitigated — but worth confirming no `|safe` usage
  - **Effort:** 15 minutes (verification)

- [ ] **SEC-015:** Avatar upload has no file size limit or validation
  - `UserUpdateForm` allows avatar upload via `request.FILES` with no file size constraint
  - A user could upload a very large image, consuming server disk/memory
  - Add `MAX_UPLOAD_SIZE` validation in the form's `clean_avatar()` method
  - **Effort:** 30 minutes

### Performance
- [ ] **PERF-002:** Session storage for demo quizzes inefficient
  - Storing full question objects instead of minimal data
  - Already mitigated with truncation (v1.5.3) but could be optimized further
  - **Effort:** 1 hour

- [ ] **PERF-003:** CDN resources not preloaded
  - Add `<link rel="preload">` for HTMX, Alpine.js, Material Icons
  - **Effort:** 30 minutes

- [ ] **PERF-006:** Synchronous AI calls block request (5-10 seconds)
  - Consider Celery/async task queue for long-running generations
  - **Effort:** 8-16 hours (significant feature)

- [ ] **PERF-007:** `generate_all_explanations` makes serial AI API calls in a loop
  - Each wrong/skipped answer triggers a separate `generate_explanation()` call (line 380-391)
  - For a 20-question quiz with many wrong answers, this could take 60+ seconds blocking the request
  - Consider batching explanations into a single prompt, or using async/concurrent calls
  - **Effort:** 2-4 hours

- [ ] **PERF-008:** `user_dashboard` aggregates stats on every page load
  - `avg_score` aggregation and `incomplete_count` filter run on every dashboard visit
  - Consider caching these values on `UserProfile` or using Django cache framework
  - **Effort:** 1-2 hours

- [ ] **PERF-009:** `submit_answer` re-queries answered IDs multiple times
  - `quiz.answers.values_list('question_id', flat=True)` is called up to 3 times per `submit_answer` call
  - Consolidate into a single query at the top of the function
  - **Effort:** 15 minutes

### Accessibility
- [ ] **A11Y-001:** Quiz options lack ARIA labels for screen readers
  - Add `aria-label` to option buttons with format "Option A: [text]"
  - **Effort:** 1 hour

- [ ] **A11Y-004:** Focus trap missing in exit modal
  - Add focus management for keyboard navigation
  - **Effort:** 1-2 hours

- [ ] **A11Y-005:** Timer not announced for screen readers
  - Add `aria-live="polite"` region for time updates
  - **Effort:** 30 minutes

### UI/UX
- [ ] **UX-001:** No loading indicators for AI generation
  - Quiz creation shows no feedback during AI processing
  - Add skeleton loader or spinner
  - **Effort:** 1-2 hours

- [x] ~~**UX-002:** Confetti animation mentioned in CHANGELOG but not visible~~
  - **FALSE:** Confetti IS implemented in `templates/quizzes/results.html` using `canvas-confetti` CDN library with multiple bursts for 100% scores.

- [ ] **UX-004:** No keyboard navigation for quiz options
  - Add keyboard shortcuts (1-4 or A-D) for option selection
  - **Effort:** 2 hours

### Testing
- [ ] **TEST-003:** Missing edge case tests
  - Empty quiz handling, API timeout scenarios, invalid model selection
  - **Effort:** 2-3 hours

### DevOps
- [ ] **OPS-001:** No health check endpoint
  - Add `/health/` endpoint for monitoring
  - **Effort:** 30 minutes

- [ ] **OPS-002:** `build.sh` doesn't call `seed_gamification` or `sync_models`/`set_active_models`
  - Deployment script runs `migrate` and creates superuser, but doesn't seed badges
  - A fresh deployment will have no badges — gamification system is silently broken
  - Add `python manage.py seed_gamification` to `build.sh`
  - **Effort:** 5 minutes

- [ ] **OPS-003:** `build.sh` uses `pip install` but project uses `uv`
  - `build.sh` installs via `pip install -r requirements.txt` (line 9)
  - Local dev uses `uv sync` per README, creating a tooling inconsistency
  - This works because Render may not have `uv`, but worth noting
  - **Effort:** 15 minutes (documentation)

---

## 📋 Low Priority (Backlog)

### Code Cleanup
- [ ] **CODE-001:** Heavy inline styles in templates
  - Stylistic issue - would require significant refactor with regression risk
- [ ] **CODE-004:** Magic numbers (well-documented with comments)
- [ ] **CLEAN-001:** Remove commented `rest_framework` in settings.py line 54
- [ ] **CLEAN-002:** Empty `models.py` files in `core` and `ai_agent` apps
- [ ] **CLEAN-003:** Empty `tests.py` files in `core` and `ai_agent` apps
- [ ] **CLEAN-004:** `quizzes/tests.py` is an empty placeholder alongside the `quizzes/tests/` directory
  - The actual tests live in `tests/test_models.py` and `tests/test_views.py`
  - The root `tests.py` file (63 bytes) serves no purpose and is confusing
  - **Effort:** 2 minutes
- [ ] **CLEAN-005:** `pyproject.toml` `python_files` config doesn't match actual test filenames
  - Config: `python_files = ["test_*.py", "*_test.py"]` — this excludes `apps/users/tests.py`
  - User tests file is named `tests.py` not `test_*.py` — yet it works because pytest discovers `TestXxx` classes
  - However, this is fragile; either rename the file or add `tests.py` to the pattern
  - **Effort:** 5 minutes
- [ ] **CLEAN-006:** Misleading import: `HttpResponse` imported from `django.shortcuts` in `quizzes/views.py`
  - Line 1: `from django.shortcuts import render, redirect, get_object_or_404, HttpResponse`
  - `HttpResponse` IS used (lines 142, 186, 290) — it is NOT unused
  - However, it's imported from `django.shortcuts` instead of `django.http` (Django re-exports it, but the import source is misleading)
  - **Effort:** 2 minutes

### Documentation
- [ ] **DOC-001:** Missing API documentation for view endpoints
- [ ] **DOC-002:** DEVELOPMENT.md testing section lacks coverage info
- [ ] **DOC-003:** Missing docstrings in several view functions
  - `create_quiz`, `quiz_player`, `submit_answer` in `quizzes/views.py` lack docstrings
- [ ] **DOC-004:** CHANGELOG missing version 1.4.0 entries (jumps 1.3.0 → 1.5.0)
- [ ] **DOC-005:** README badge says "Django-5.2.8" but `pyproject.toml` specifies `django>=5.2.8`
  - Version could drift; badge should either be dynamic or track `pyproject.toml`
- [ ] **DOC-006:** README test credentials (`admin@example.com` / `password123`) are misleading
  - These are only created if `DJANGO_SUPERUSER_EMAIL` env var is set during `build.sh`
  - On a fresh local dev setup, these credentials won't exist
- [ ] **DOC-007:** DEVELOPMENT.md says "9 total" models but there are exactly 9 — this is correct but fragile
  - If models are added/removed, the hardcoded count will be wrong
- [ ] **DOC-008:** DEVELOPMENT.md references `check_models.py` with `uv run check_models.py` but doesn't mention `cd qtrmrs/` first
  - From the project root, `check_models.py` is at `qtrmrs/check_models.py`
- [ ] **DOC-009:** `QUIZ_RATE_LIMIT` env var defined in `.env.example` and settings but never used
  - `settings.py` line 238 reads `QUIZ_RATE_LIMIT` from env, but rate limits are hardcoded as `'10/m'` in decorators
  - Either wire up the setting or remove the env var
  - **Effort:** 15 minutes

### Anomalies
- [ ] **ANOM-001:** `Badge.requirement_type` uses `'quizzes'` in test fixture but `check_and_award_badges` doesn't handle it
  - `gamification.py` checks for `'level'`, `'streak'`, `'score'`, `'correct'` — but never `'quizzes'`
  - The test fixture creates a badge with `requirement_type='quizzes'` that can never be earned
  - Either add quiz-count logic to `check_and_award_badges`, or remove the test badge
  - **Effort:** 30 minutes

- [ ] **ANOM-002:** `UserProfile.preferred_difficulty` defaults to `'Intermediate'` (capitalized)
  - All other difficulty handling normalizes to lowercase `'intermediate'`
  - Inconsistent casing could cause mismatches if the preference is ever used for quiz defaults
  - **Effort:** 5 minutes

- [ ] **ANOM-003:** `generate_explanation` error handling duplicates `_handle_error` logic
  - `services.py` line 234 re-checks for 429/quota errors inline instead of using `_handle_error()`
  - This creates maintenance burden — error classification logic exists in two places
  - **Effort:** 15 minutes

- [ ] **ANOM-004:** Async methods in `QuizGenerator` are unused
  - `generate_quiz_async`, `parse_intent_async`, etc. exist but are never called anywhere
  - WSGI application (`config/wsgi.py`) is used in production, not ASGI — async methods are dead code
  - Consider removing until ASGI is actually adopted
  - **Effort:** 10 minutes

- [ ] **ANOM-005:** `LOGGING` config defines unused `json` formatter
  - `settings.py` line 257 defines a `json` formatter but no handler uses it
  - Either remove or wire it up for production structured logging
  - **Effort:** 5 minutes

### Accessibility
- [ ] **A11Y-002:** Timer announcements for screen readers missing
- [ ] **A11Y-003:** Code snippets in quizzes need better contrast ratios

### Testing
- [ ] **TEST-004:** No E2E browser tests (Playwright)

### Future Enhancements
- [ ] PWA support with service worker
- [ ] Leaderboards
- [ ] Export/Share Results (JSON/CSV)
- [ ] Export results as PDF
- [ ] Resume Analysis Skill Extraction
- [ ] Voice Mode for technical interviews
- [ ] GitHub Actions CI/CD pipeline

---

## 🏗️ Architecture Notes

- Service-Oriented logic in `apps/ai_agent/services.py`
- HTMX for single-page interactivity without high JS overhead
- Custom User model with email as primary identifier
- Gamification system: XP, Levels (1-∞), Streaks, 9 Badge types
- Unified `settings.py` with DEBUG-based toggling for production security
- Rate limiting via `django-ratelimit` decorator
- CSP headers enforced via `django-csp` in production

---
