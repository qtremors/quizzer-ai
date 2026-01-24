# Quizzer AI - Tasks

> **Project:** Quizzer AI  
> **Version:** 1.5.1  
> **Last Updated:** 2026-01-23  
> **Last Review:** Comprehensive Codebase Review

---

## � Critical (High Priority)

### Security
- [x] **SEC-001:** CSP headers defined but not enforced - Missing `django-csp` middleware integration
  - ✅ Added `django-csp` package and CSP middleware in production
- [x] **SEC-002:** Missing password reset flow - No forgot password functionality
  - ✅ Implemented with Django auth views and custom templates (30-min token expiry)
- [x] **SEC-003:** Missing email verification on signup
  - ✅ Implemented with warning banner for unverified users
- [x] **SEC-004:** Demo quiz session data not size-limited
  - ✅ Added limits: max 10 questions, text truncation, option limits

### Bugs
- [ ] **BUG-001:** `ratelimited_view` uses inline HTML instead of template
  - `core/views.py:16-27` - Inline styled HTML hardcoded in view function
- [ ] **BUG-002:** `quick_quiz` level mismatch - Uses 'Easy' string but model expects lowercase 'beginner'
  - `quizzes/views.py:477` - `level='Easy'` should be `level='beginner'`
- [ ] **BUG-003:** Missing @login_required on `demo_submit` and `demo_player`
  - Not a bug per se, but these views lack `@require_http_methods` decorator consistency

---

## ⚠️ Medium Priority

### Code Quality
- [ ] **CODE-001:** Heavy inline styles in templates
  - `base.html:64,76,79,80,86,90-96,105,109` - Inline styles should be CSS classes
  - `player.html:35,41,44,62,66,70,72` - Same issue
- [ ] **CODE-002:** Inconsistent import of `AIError`
  - `ai_agent/views.py:79` imports `AIError` inside function instead of at top
- [ ] **CODE-003:** Duplicate `asyncio` imports in async methods
  - `services.py:236,249,256,262,271` - Import at top-level instead
- [ ] **CODE-004:** Magic numbers scattered in code
  - `views.py:37` (500), `views.py:71` (100/200/255), `gamification.py:27` (10), etc.
- [ ] **CODE-005:** Debug logging left in production code
  - `quizzes/views.py:574-575` - `logger.info` with full question data
- [ ] **CODE-006:** Unused imports - `IntegrityError` imported but not used in `quizzes/views.py:5`

### Architecture
- [ ] **ARCH-001:** Quiz creation logic duplicated across 3 views
  - `create_quiz`, `process_chat_message`, `quick_quiz` share similar patterns
  - Consider extracting to a service function
- [ ] **ARCH-002:** View files too large - `quizzes/views.py` is 650 lines
  - Split into setup, player, results, demo modules
- [ ] **ARCH-003:** Missing model managers
  - `Quiz.objects.filter(user=request.user).order_by('-created_at')` repeated
  - Create `QuizQuerySet` with `for_user()` method
- [ ] **ARCH-004:** Gamification coupling - Profile updates tightly coupled in `submit_answer`
  - Consider signals or separate service for XP/badge logic

### Performance
- [ ] **PERF-001:** N+1 query potential in `quiz_results`
  - `UserAnswer.objects.filter(quiz=quiz)` then iterating - need `prefetch_related('question__options')`
- [ ] **PERF-002:** Session storage for demo quizzes inefficient
  - Storing full question objects instead of just minimal data
- [ ] **PERF-003:** CDN resources not preloaded
  - HTMX, Alpine.js, Prism.js lack `preload` hints for better LCP
- [ ] **PERF-004:** Missing database indexes for common queries
  - `UserProfile.user` could benefit from additional compound indexes

### UI/UX
- [ ] **UX-001:** No loading states for AI generation
  - Quiz creation shows no feedback while AI generates questions
- [ ] **UX-002:** Confetti animation mentioned in CHANGELOG but not visible in results
  - Feature may be incomplete or CSS not properly loaded
- [ ] **UX-003:** Mobile dropdown positioning fixed but may overlap content
  - `base.css:352-357` fixes need verification on small screens
- [ ] **UX-004:** No keyboard navigation for quiz options
  - Options are labels/buttons but lack proper keyboard shortcuts (1-4)

### Testing
- [ ] **TEST-001:** No tests for `ai_agent` module - `tests.py` is empty placeholder
- [ ] **TEST-002:** No integration tests for AI service with mocked responses
- [ ] **TEST-003:** Missing edge case tests
  - Empty quiz handling, API timeout scenarios, invalid model selection
- [ ] **TEST-004:** No E2E browser tests (Playwright) - listed as future

---

## � Low Priority

### Code Cleanup
- [ ] **CLEAN-001:** Remove commented code in `base.py:34` (rest_framework)
- [ ] **CLEAN-002:** Empty `models.py` in `core` and `ai_agent` apps
- [ ] **CLEAN-003:** Unused `tests.py` files in `core` and `ai_agent`
- [ ] **CLEAN-004:** `check_models.py` in root - appears to be debug script

### Documentation
- [ ] **DOC-001:** Missing API documentation for view endpoints
- [ ] **DOC-002:** DEVELOPMENT.md testing section lacks coverage info
- [ ] **DOC-003:** Missing docstrings in several view functions
  - `create_quiz`, `submit_answer` need better documentation
- [ ] **DOC-004:** CHANGELOG missing version 1.4.0 entries
  - Jumps from 1.3.0 to 1.5.0

### Accessibility
- [ ] **A11Y-001:** Quiz options lack ARIA labels for screen readers
- [ ] **A11Y-002:** Timer announcements for screen readers missing
- [ ] **A11Y-003:** Code snippets in quizzes need better contrast ratios
- [ ] **A11Y-004:** Focus trap missing in exit modal

### Future Enhancements
- [ ] PWA support with service worker
- [ ] Leaderboards
- [ ] Export/Share Results (JSON/CSV)
- [ ] Export results as PDF
- [ ] Resume Analysis Skill Extraction
- [ ] Voice Mode for technical interviews

---

## 🏗️ Architecture Notes

- Service-Oriented logic in `apps/ai_agent/services.py`
- HTMX for single-page interactivity without high JS overhead
- Custom User model with email as primary identifier
- Gamification system: XP, Levels (1-∞), Streaks, 9 Badge types
- Split settings: unified `settings.py` with DEBUG-based toggling for production security
- Rate limiting via `django-ratelimit` decorator

---

## 📊 Code Metrics (from review)

| Component | Files | Lines | Test Coverage |
|-----------|-------|-------|---------------|
| `ai_agent` | 10 | ~550 | 0% (no tests) |
| `quizzes` | 12 | ~1050 | ~60% |
| `users` | 9 | ~650 | ~70% |
| `core` | 7 | ~100 | 0% |
| **Total** | 38 | ~2350 | ~40% (est.) |

---
