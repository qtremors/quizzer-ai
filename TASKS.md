# Quizzer AI — Tasks

> **Version:** 1.6.6  
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
- [ ] **TEST-004:** No tests for demo flow (`quick_quiz`, `demo_player`, `demo_submit`, `demo_results`)
- [ ] **TEST-005:** No tests for `create_quiz` or `process_chat_message` views
- [ ] **TEST-006:** No test coverage for `award_quiz_completion` service

### Architecture & Design
- [ ] **ARCH-008:** `award_quiz_completion` in `quizzes/services.py` creates circular dependency with `users` app — currently mitigated by lazy imports (standard Django pattern)

---

## 📋 Low Priority (Backlog)

### Accessibility
- [ ] **A11Y-002:** Timer announcements for screen readers missing
- [ ] **A11Y-003:** Code snippets need better contrast ratios

---

## 🔍 PR Review Findings

### Security & Robustness
- [x] **PR-001:** `sync_models.py` (lines 17-18) - Move `get_gemini_client()` inside the `try` block to handle `ValueError` properly.
- [x] **PR-002:** `models.py` (lines 14-23) - Wrap `AIModel.save()` default-reset logic in `transaction.atomic()` with `select_for_update()` and add DB-level `UniqueConstraint` for `is_default=True`.
- [x] **PR-003:** `core/views.py` (lines 28-29) - Narrow generic `except Exception:` in `health_check` to `except DatabaseError:`.
- [x] **PR-004:** `quizzes/templatetags/quiz_filters.py` (lines 10-12) - Update `format_time` to safely coerce `seconds` (check isinstance/try-except) to avoid `ValueError`.
- [x] **PR-005:** `quizzes/views/demo.py` - `quick_quiz` performs writes on a `GET` endpoint. Prefer `POST` or split guest/authenticated endpoints.
- [x] **PR-006:** `quizzes/views/demo.py` (lines 89-97) - Normalize option shapes and stringify/truncate to prevent breaking answer matching in session.
- [x] **PR-007:** `quizzes/views/results.py` (lines 101-104) - Use `strict=True` with `zip()` and check lengths before `bulk_update` to prevent silent partial updates.
- [x] **PR-008:** `users/signup.html` (lines 42-43) - Remove `|safe` filter from `{{ field.help_text|safe }}` to prevent XSS.

### Accessibility (A11Y)
- [x] **PR-009:** `ai_agent/partials/chat_error.html` (lines 1-18) - Add `role="alert"` or `aria-live` to error bubble for screen readers.
- [x] **PR-010:** `quizzes/demo_player.html` (lines 66-70) - Replace `display: none` on radio inputs with visually-hidden CSS pattern so they remain focusable.
- [x] **PR-011:** `quizzes/setup.html` (lines 28-31) - Add `for` attributes to labels and map them to input/select `id`s.
- [x] **PR-012:** `users/dashboard.html` (lines 109-116) - Add descriptive `aria-label` attributes to icon-only action buttons (Retry, Delete).

### UI/UX & Routing
- [x] **PR-013:** `core/languages.html` (lines 95-96) - URL encode the `C++` language query parameter (`C%2B%2B`) to avoid it parsing as space.
