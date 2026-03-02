# Quizzer AI — Tasks

> **Version:** 1.6.5  
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
