# Quizzer AI - Tasks

> **Project:** Quizzer AI  
> **Version:** 1.5.3  
> **Last Updated:** 2026-01-24  
> **Last Review:** Comprehensive End-to-End Codebase Review

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

- [ ] **CODE-010:** Settings.py line 150 has typo in DEFAULT_AI_MODEL default
  - Currently: `gemini-flash-litelatest` (missing hyphen)
  - Should be: `gemini-flash-lite-latest`
  - **Effort:** 5 minutes

---

## ⚠️ Medium Priority (Next Sprint)

### Architecture
- [ ] **ARCH-002:** View files too large - `quizzes/views.py` is 649 lines
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

### Security
- [ ] **SEC-006:** `'unsafe-inline'` in CSP script-src
  - Weakens XSS protection but required for HTMX/Alpine.js inline code
  - Consider nonces in future for tighter security
  - **Effort:** 4-6 hours (significant refactor)

- [ ] **SEC-008:** No rate limiting on password reset endpoint
  - Add `@ratelimit(key='ip', rate='5/h')` to prevent enumeration
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

- [ ] **UX-002:** Confetti animation mentioned in CHANGELOG but not visible
  - Feature may be incomplete or CSS not loaded
  - Verify and fix or remove from CHANGELOG
  - **Effort:** 30 minutes

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

---

## 📋 Low Priority (Backlog)

### Code Cleanup
- [ ] **CODE-001:** Heavy inline styles in templates
  - Stylistic issue - would require significant refactor with regression risk
- [ ] **CODE-004:** Magic numbers (well-documented with comments)
- [ ] **CLEAN-001:** Remove commented `rest_framework` in settings.py line 54
- [ ] **CLEAN-002:** Empty `models.py` files in `core` and `ai_agent` apps
- [ ] **CLEAN-003:** Empty `tests.py` files in `core` and `ai_agent` apps

### Documentation
- [ ] **DOC-001:** Missing API documentation for view endpoints
- [ ] **DOC-002:** DEVELOPMENT.md testing section lacks coverage info
- [ ] **DOC-003:** Missing docstrings in several view functions
- [ ] **DOC-004:** CHANGELOG missing version 1.4.0 entries (jumps 1.3.0 → 1.5.0)

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
