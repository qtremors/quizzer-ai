# Quizzer AI — Tasks

> **Version:** 1.6.3  
> **Last Updated:** 2026-03-02

---

## 🔴 High Priority

### Security
- [ ] **SEC-016:** `demo_submit` has no rate limiting on demo submissions allowing rapid session writes
- [ ] **SEC-017:** `delete_quiz` uses `topic_description` in messages — potential stored XSS if `|safe` is ever added to templates
- [ ] **SEC-018:** Gemini API key cached in module-level `_client` global — no mechanism to invalidate if key is rotated
- [ ] **SEC-019:** `sync_models` management command creates its own `genai.Client` instead of using `get_gemini_client()`

---

## 🟠 Medium Priority

### Security
- [ ] **SEC-006:** `'unsafe-inline'` in CSP script-src — required for HTMX/Alpine.js; consider nonces in future
- [ ] **SEC-020:** `quick_quiz` is rate-limited by IP only (`key='ip'`) — behind a shared proxy, all users share the same limit

### Correctness & Reliability
- [ ] **BUG-013:** `quiz_results` recalculation guard misses legitimate 0% scores — cosmetic only
- [ ] **BUG-014:** `generate_batch_explanations` doesn't validate that each AI response element is a string
- [ ] **BUG-015:** `format_duration` may produce nonsensical output for negative values

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
- [ ] **ARCH-007:** `Question.objects.create()` per-question inside loop — should use `bulk_create`
- [ ] **ARCH-008:** `award_quiz_completion` in `quizzes/services.py` creates circular dependency with `users` app

---

## 📋 Low Priority (Backlog)

### Documentation
- [ ] **DOC-001:** Missing API documentation for view endpoints
- [ ] **DOC-010:** `DEVELOPMENT.md` lists `DATABASE_URL` as required but local dev can now use SQLite fallback
- [ ] **DOC-012:** CHANGELOG v1.3.0 says "9 Achievement Badges" — hardcoded count may drift

### Accessibility
- [ ] **A11Y-002:** Timer announcements for screen readers missing
- [ ] **A11Y-003:** Code snippets need better contrast ratios

### Maintainability & Code Quality
- [ ] **CLEAN-009:** `base.html` CSRF token in script — should add explicit context processor
- [ ] **CLEAN-010:** `UserProfile.xp_for_next_level` naming is misleading
- [ ] **CLEAN-011:** `check_models.py` is standalone script — consider converting to management command

### Configuration & Infrastructure
- [ ] **CFG-002:** `build.sh` doesn't run `sync_models` — new Gemini models won't auto-populate
- [ ] **CFG-003:** No `CACHES` setting — dashboard cache uses non-persistent `LocMemCache` by default
