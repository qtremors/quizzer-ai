# Quizzer AI - Issues & Tasks

This file tracks all identified bugs, inconsistencies, and improvements from code review.

---

## � High Priority - Bugs & Logic Issues

### 1. Quick Quiz Key Mismatch (Bug)
**File:** `quizzes/views.py` lines 481-499
**Problem:** `create_quiz` saves questions with key `text` (line 117), but `quick_quiz` reads from AI response and uses `question` key (line 484 vs line 571). Inconsistent key handling between logged-in and guest paths.
**Impact:** Demo questions may fail to display properly if AI returns inconsistent keys.
**Fix:** Normalize to a single key (`text`) in AI response parsing.

### 2. Demo Quiz Missing Timer
**File:** `quizzes/demo_player.html`
**Problem:** Demo quiz player has no timer tracking, unlike the main player. Guests experience inconsistent UX.
**Fix:** Add session-based timer for demo mode.

### 3. Bare Exception in Quick Quiz
**File:** `quizzes/views.py` lines 437-438
**Problem:** `except:` with no exception type is a code smell and can mask unexpected errors.
**Fix:** Use `except Exception as e:` and log the specific error.

### 4. Retry Quiz Doesn't Reset Gamification
**File:** `quizzes/views.py` lines 385-404
**Problem:** `retry_quiz` clears answers but gamification already awarded XP on first completion. Retaking awards XP again.
**Impact:** XP farming exploit.
**Fix:** Either don't award XP on retries or track quiz retake status.

### 5. Missing Database Migration Check
**File:** No migration for `UserProfile` fields added in gamification
**Problem:** If new fields were added without proper migration, deployments could fail.
**Fix:** Verify all model fields have corresponding migrations with `python manage.py showmigrations`.

---

## 🟡 Medium Priority - Code Quality

### 6. Signup Password Helper Text Hidden
**File:** `users/signup.html`
**Problem:** Help text only shows on focus, but validation rules are important upfront.
**Fix:** Always-visible password requirements or show on first interaction.

### 7. Dashboard Stats Limited
**File:** `users/dashboard.html`
**Problem:** Dashboard shows XP/level/streak in profile but could integrate better with main stats section.
**Suggestion:** Show "Best Score" from profile.best_score, "Current Streak", "Total Correct Answers".

### 8. No Skip Confirmation
**File:** `quizzes/partials/question_card.html` line 30
**Problem:** Skip button immediately skips with no confirmation.
**Suggestion:** Optional modal "Are you sure?" for accidental clicks.

### 9. Import Inside Function (Performance)
**Files:** `quizzes/views.py` lines 228-232, 411, 442, 455, 457, 463
**Problem:** Imports like `from apps.users.gamification import ...` inside functions reduce readability and add minor overhead.
**Fix:** Move to top-level imports.

### 10. CSS `!important` Overuse
**File:** `quizzes/partials/question_card.html` lines 211-219
**Problem:** Multiple `!important` declarations on Prism code block.
**Fix:** Increase CSS specificity or load app styles after Prism.

### 11. Heavy Inline Styles
**Files:** `base.html`, `setup.html`, `player.html`, `results.html`
**Problem:** Significant inline `style="..."` usage makes global theming difficult.
**Fix:** Extract patterns to CSS classes like `.page-container`, `.section-header`, etc.

### 12. Duplicate Time Formatting Logic
**Files:** `quizzes/views.py` quiz_results (lines 306-311), could be duplicated elsewhere
**Problem:** Time formatting logic is inline rather than in a utility.
**Fix:** Create `utils.py` with `format_duration(seconds)` helper.

### 13. Model Without Ordering
**File:** `quizzes/models.py` - `UserAnswer` model
**Problem:** `UserAnswer` has no default `ordering` in Meta, which can lead to unpredictable iteration.
**Fix:** Add `ordering = ['id']` to `UserAnswer.Meta`.

---

## 🟢 Low Priority - Polish & Improvements

### 14. Language Grid Search/Filter
**File:** `core/languages.html`
**Problem:** As more languages are added, browsing becomes slower.
**Suggestion:** Add search bar or category filters (Web, Backend, Database, etc.).

### 15. No Focus Ring Styling on Some Inputs
**Files:** Various templates
**Problem:** Some form elements may not have visible focus indicators for keyboard users.
**Fix:** Audit `:focus-visible` coverage, ensure all inputs have visible focus styles.

### 16. Missing Alt Text on Some Images
**File:** `base.html` line 83-84
**Problem:** Avatar image has minimal alt text.
**Fix:** Add descriptive alt like `alt=\"{{ user.username }}'s avatar\"`.

### 17. AI Model Could Fallback Smarter
**File:** `ai_agent/services.py` line 34
**Problem:** Uses hardcoded fallback `'gemini-flash-latest'` if no setting.
**Suggestion:** Query available models or use a validated, tested default.

### 18. No Logging in Client Module
**File:** `ai_agent/client.py`
**Problem:** Silent ValueError if API key missing - should log before raising.
**Fix:** Add logging before the raise statement.

### 19. Test Coverage Gaps
**Files:** `apps/core/tests.py`, `apps/users/tests.py`, `apps/ai_agent/tests.py`
**Problem:** These test files appear empty or minimal.
**Fix:** Add tests for:
  - User signup/login flows
  - Profile creation signal
  - Gamification XP/level calculations
  - Badge awarding logic
  - AI service mocking

---

## 📦 Missing Features (from code analysis)

### 20. Settings Page Missing Learning Interests UI
**File:** `users/settings.html`
**Problem:** `UserProfile.learning_interests` field exists but no UI to set them.
**Fix:** Add a multi-select or tag input for learning interests on settings page.

### 21. Badge Display Missing
**File:** `users/dashboard.html`
**Problem:** `UserBadge` model exists but badges aren't displayed on dashboard.
**Fix:** Query `user.earned_badges.all()` and display with icons.

### 22. No Password Reset Flow
**Files:** `users/` directory
**Problem:** No forgot password or password reset functionality.
**Fix:** Implement Django's password reset views with email.

### 23. No Email Verification
**File:** `users/views.py`
**Problem:** Users can sign up with any email without verification.
**Fix:** Add email verification flow before account activation.

### 24. Quiz Deletion Missing
**Files:** `quizzes/views.py`, templates
**Problem:** Users cannot delete their quizzes from dashboard.
**Fix:** Add delete button with confirmation modal.

### 25. No Export/Share Results
**File:** `quizzes/results.html`
**Problem:** No way to export or share quiz results.
**Fix:** Add "Copy Link" or "Export PDF" buttons.

---

## 🔧 Efficiency & Resource Usage

### 26. Options Created One-by-One in Quick Quiz
**File:** `quizzes/views.py` lines 495-499
**Problem:** `Option.objects.create()` in loop instead of `bulk_create()` like in `create_quiz`.
**Fix:** Collect options and use `bulk_create()` for fewer DB queries.

### 27. Session Data Could Grow Large
**File:** `quizzes/views.py` lines 504-510
**Problem:** Demo quiz stores questions in session. If AI generates verbose responses, session grows.
**Suggestion:** Store only essential fields or set session expiry.

### 28. File Logging Handler Not Used
**File:** `config/settings/base.py` lines 144-148
**Problem:** File handler 'file' is defined but not attached to any logger (only 'console' is used).
**Fix:** Add 'file' handler to loggers if production logging is desired.

---

## 📖 Documentation Gaps

### 29. README Badge Count Outdated
**File:** `README.md` line 9
**Problem:** Badge shows "15 passing" but test count may have changed.
**Fix:** Update or use dynamic badge from CI.

### 30. Missing API Documentation
**Problem:** No docs for HTMX endpoints, view parameters, or expected responses.
**Fix:** Add API section to README or create `docs/API.md`.

### 31. Missing Deployment Guide
**Problem:** No instructions for production deployment (Gunicorn, Nginx, env vars).
**Fix:** Add "Deployment" section to README.

### 32. Missing CONTRIBUTING.md
**Problem:** Contributing section in README is brief, no detailed guide.
**Fix:** Create `CONTRIBUTING.md` with code style, PR process, testing requirements.

---

## ✅ Recently Fixed (v1.1.1+)

### Code Review Fixes
- [x] **Theme Flash Fix** - Inline script applies theme before Alpine.js loads
- [x] **Slider Theme Fix** - Toggle uses theme-aware CSS variables
- [x] **Dropdown Styling** - Theme-aware hover states, SVG arrows on selects
- [x] **Viewport Protection** - All UI elements constrained to viewport
- [x] **Type Comparison Fix** - Option matching now normalizes to strings
- [x] **Removed `is_study_mode`** - Cleaned up stale model field
- [x] **Dashboard Pagination** - Added page controls

---

## ✅ Fixed (v1.1.0)

### Features
- [x] Dark/Light Theme Toggle
- [x] Toast Notifications
- [x] Skeleton Loaders
- [x] Mobile Optimization
- [x] Accessibility (skip link, focus-visible, ARIA)
- [x] Timer Per Question
- [x] Structured Logging
- [x] Unit Tests (pytest)

---

## 🔮 Future Ideas (Backlog)

- [x] Confetti animation on 100% score ✅ v1.3.0
- [x] Daily streaks gamification ✅ v1.3.0
- [x] XP & Leveling system ✅ v1.3.0
- [x] Achievement badges ✅ v1.3.0
- [x] Quick Quiz demo mode ✅ v1.3.0
- [ ] Settings page with learning interests UI
- [ ] Badge display on dashboard/profile
- [ ] PWA support with service worker
- [ ] Leaderboards
- [ ] Export results as PDF
- [ ] Topic recommendations based on weak areas
- [ ] E2E tests with Playwright
- [ ] Quiz categories/tags
- [ ] Social sharing
- [ ] Multiple correct answers support
- [ ] Timed quizzes (countdown mode)
- [ ] Study mode (no scoring, just learning)
