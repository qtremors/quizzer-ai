# Quizzer AI — Tasks

> **Version:** 1.6.0  
> **Last Updated:** 2026-03-02

---

## 🟠 Medium Priority

### Security
- [ ] **SEC-006:** `'unsafe-inline'` in CSP script-src — required for HTMX/Alpine.js; consider nonces in future

### Performance
- [ ] **PERF-006:** Synchronous AI calls block request (5–10s) — consider Celery/async task queue

### Accessibility
- [ ] **A11Y-001:** Quiz options lack `aria-label` for screen readers
- [ ] **A11Y-004:** Focus trap missing in exit modal — add focus management for keyboard nav
- [ ] **A11Y-005:** Timer not announced for screen readers — add `aria-live="polite"` region

### UI/UX
- [ ] **UX-001:** No loading indicators for AI generation — add skeleton loader or spinner
- [ ] **UX-004:** No keyboard navigation for quiz options — add shortcuts (1–4 or A–D)

### Testing
- [ ] **TEST-003:** Missing edge case tests — empty quiz handling, API timeouts, invalid model selection

### DevOps
- [ ] **OPS-001:** No health check endpoint — add `/health/`
- [ ] **OPS-002:** `build.sh` doesn't seed gamification data
- [ ] **OPS-003:** `build.sh` uses `pip install` but project uses `uv` — document inconsistency

---

## 📋 Low Priority (Backlog)

### Code Cleanup
- [ ] **CLEAN-001:** Remove commented `rest_framework` in `settings.py`
- [ ] **CLEAN-002:** Empty `models.py` in `core` app
- [ ] **CLEAN-003:** Empty `tests.py` in `core` app
- [ ] **CLEAN-004:** `quizzes/tests.py` is an empty placeholder alongside `quizzes/tests/` directory
- [ ] **CLEAN-005:** `pyproject.toml` `python_files` config doesn't match `tests.py` naming convention
- [ ] **CLEAN-006:** `HttpResponse` imported from `django.shortcuts` instead of `django.http`

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

### Anomalies
- [ ] **ANOM-001:** `Badge.requirement_type='quizzes'` in fixture but handler doesn't support it
- [ ] **ANOM-002:** `UserProfile.preferred_difficulty` defaults to `'Intermediate'` (capitalized) — inconsistent
- [ ] **ANOM-003:** `generate_explanation` error handling duplicates `_handle_error` logic
- [ ] **ANOM-004:** Async methods in `QuizGenerator` are unused (WSGI, not ASGI) — dead code
- [ ] **ANOM-005:** `LOGGING` config defines unused `json` formatter

### Accessibility
- [ ] **A11Y-002:** Timer announcements for screen readers missing
- [ ] **A11Y-003:** Code snippets need better contrast ratios

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
- Gamification system: XP, Levels (1–∞), Streaks, 9 Badge types
- Unified `settings.py` with DEBUG-based toggling for production security
- Rate limiting via `django-ratelimit` decorator
- CSP headers enforced via `django-csp` in production
