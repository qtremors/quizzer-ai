# Quizzer AI - Tasks

> **Project:** Quizzer AI  
> **Version:** 1.5.8  
> **Last Updated:** 2026-02-27

---

## ⚠️ Medium Priority

### Architecture
- [x] **ARCH-002:** View files too large — `quizzes/views.py` is 616 lines
  - Split into: `setup.py`, `player.py`, `results.py`, `demo.py`
  - **Effort:** 2-4 hours

- [x] **ARCH-003:** Missing model managers
  - `Quiz.objects.filter(user=request.user).order_by('-created_at')` repeated 4 times
  - Create `QuizQuerySet` with `for_user()` method
  - **Effort:** 1 hour

- [x] **ARCH-004:** Gamification coupling in `submit_answer`
  - Profile updates tightly coupled (lines 241-288)
  - Consider Django signals or separate service for XP/badge logic
  - **Effort:** 2-3 hours

- [x] **ARCH-005:** `AIModel` model lives in `quizzes` app but logically belongs in `ai_agent`
  - Both `ai_agent` views and management commands import it from `quizzes`
  - Consider moving to `ai_agent/models.py` (currently empty)
  - **Effort:** 1-2 hours (requires migration)

- [x] **ARCH-006:** `Badge` and `UserBadge` admin registrations missing
  - `users/admin.py` only registers `User` — `UserProfile`, `Badge`, `UserBadge` not registered
  - **Effort:** 15 minutes

### Security
- [ ] **SEC-006:** `'unsafe-inline'` in CSP script-src
  - Required for HTMX/Alpine.js inline code; consider nonces in future
  - **Effort:** 4-6 hours (significant refactor)

- [ ] **SEC-008:** No rate limiting on password reset endpoint
  - Add `@ratelimit(key='ip', rate='5/h')` to prevent enumeration
  - **Effort:** 30 minutes

- [ ] **SEC-013:** `CSRF_COOKIE_HTTPONLY = True` may break HTMX CSRF on cached pages
  - Currently mitigated by server-side template tag; latent risk — document the dependency
  - **Effort:** 30 minutes (documentation/testing)

- [ ] **SEC-014:** Verify `username` rendering is auto-escaped (no `|safe` usage)
  - Django auto-escapes by default; confirm no bypass exists
  - **Effort:** 15 minutes (verification)

- [ ] **SEC-015:** Avatar upload has no file size limit or validation
  - Add `MAX_UPLOAD_SIZE` validation in `clean_avatar()` method
  - **Effort:** 30 minutes

### Performance
- [ ] **PERF-002:** Session storage for demo quizzes inefficient
  - Storing full question objects; partially mitigated with truncation (v1.5.3)
  - **Effort:** 1 hour

- [ ] **PERF-003:** CDN resources not preloaded
  - Add `<link rel="preload">` for HTMX, Alpine.js, Material Icons
  - **Effort:** 30 minutes

- [ ] **PERF-006:** Synchronous AI calls block request (5-10 seconds)
  - Consider Celery/async task queue for long-running generations
  - **Effort:** 8-16 hours (significant feature)

- [ ] **PERF-007:** `generate_all_explanations` makes serial AI API calls in a loop
  - For a 20-question quiz with many wrong answers, could take 60+ seconds
  - Consider batching into a single prompt or using concurrent calls
  - **Effort:** 2-4 hours

- [ ] **PERF-008:** `user_dashboard` aggregates stats on every page load
  - Consider caching on `UserProfile` or using Django cache framework
  - **Effort:** 1-2 hours

- [ ] **PERF-009:** `submit_answer` re-queries answered IDs multiple times
  - Consolidate `quiz.answers.values_list(...)` into a single query
  - **Effort:** 15 minutes

### Accessibility
- [ ] **A11Y-001:** Quiz options lack ARIA labels for screen readers
  - Add `aria-label` to option buttons
  - **Effort:** 1 hour

- [ ] **A11Y-004:** Focus trap missing in exit modal
  - Add focus management for keyboard navigation
  - **Effort:** 1-2 hours

- [ ] **A11Y-005:** Timer not announced for screen readers
  - Add `aria-live="polite"` region for time updates
  - **Effort:** 30 minutes

### UI/UX
- [ ] **UX-001:** No loading indicators for AI generation
  - Add skeleton loader or spinner during quiz creation
  - **Effort:** 1-2 hours

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

- [ ] **OPS-002:** `build.sh` doesn't seed gamification data
  - Add `python manage.py seed_gamification` to `build.sh`
  - **Effort:** 5 minutes

- [ ] **OPS-003:** `build.sh` uses `pip install` but project uses `uv`
  - Tooling inconsistency; works on Render but worth documenting
  - **Effort:** 15 minutes (documentation)

---

## 📋 Low Priority (Backlog)

### Code Cleanup
- [ ] **CLEAN-001:** Remove commented `rest_framework` in `settings.py` line 54
- [ ] **CLEAN-002:** Empty `models.py` files in `core` and `ai_agent` apps
- [ ] **CLEAN-003:** Empty `tests.py` in `core` app (ai_agent one already removed in v1.5.6)
- [ ] **CLEAN-004:** `quizzes/tests.py` is an empty placeholder alongside the `quizzes/tests/` directory
  - **Effort:** 2 minutes
- [ ] **CLEAN-005:** `pyproject.toml` `python_files` config doesn't match `apps/users/tests.py` naming
  - Config expects `test_*.py` but user tests use `tests.py`; works by class discovery but is fragile
  - **Effort:** 5 minutes
- [ ] **CLEAN-006:** `HttpResponse` imported from `django.shortcuts` instead of `django.http`
  - Not broken (Django re-exports it) but misleading import source
  - **Effort:** 2 minutes

### Documentation
- [ ] **DOC-001:** Missing API documentation for view endpoints
- [ ] **DOC-002:** DEVELOPMENT.md testing section lacks coverage info
- [ ] **DOC-003:** Missing docstrings in `create_quiz`, `quiz_player`, `submit_answer`
- [ ] **DOC-004:** CHANGELOG missing version 1.4.0 entries (jumps 1.3.0 → 1.5.0)
- [ ] **DOC-005:** README badge says "Django-5.2.8" — should track `pyproject.toml`
- [ ] **DOC-006:** README test credentials only exist if env var is set during `build.sh`
- [ ] **DOC-007:** DEVELOPMENT.md hardcodes "9 total" models — fragile
- [ ] **DOC-008:** DEVELOPMENT.md `check_models.py` command missing `cd qtrmrs/`
- [ ] **DOC-009:** `QUIZ_RATE_LIMIT` env var defined in settings but never wired to decorators
  - Either use `settings.QUIZ_RATE_LIMIT` in rate limit decorators or remove the env var
  - **Effort:** 15 minutes

### Anomalies
- [ ] **ANOM-001:** `Badge.requirement_type='quizzes'` in test fixture but handler doesn't support it
  - Either add quiz-count logic to `check_and_award_badges` or fix the fixture
  - **Effort:** 30 minutes

- [ ] **ANOM-002:** `UserProfile.preferred_difficulty` defaults to `'Intermediate'` (capitalized)
  - All other difficulty handling normalizes to lowercase
  - **Effort:** 5 minutes

- [ ] **ANOM-003:** `generate_explanation` error handling duplicates `_handle_error` logic
  - Line 234 re-checks for 429/quota inline instead of using `_handle_error()`
  - **Effort:** 15 minutes

- [ ] **ANOM-004:** Async methods in `QuizGenerator` are unused (WSGI, not ASGI)
  - Dead code — consider removing until ASGI is adopted
  - **Effort:** 10 minutes

- [ ] **ANOM-005:** `LOGGING` config defines unused `json` formatter
  - Either remove or wire up for production structured logging
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

- Service layer: `quizzes/services.py` and `ai_agent/services.py`
- HTMX for single-page interactivity without heavy JS overhead
- Custom User model with email as primary identifier
- Gamification system: XP, Levels (1-∞), Streaks, 9 Badge types
- Unified `settings.py` with DEBUG-based toggling for production security
- Rate limiting via `django-ratelimit` decorator
- CSP headers enforced via `django-csp` in production

---
