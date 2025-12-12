# Quizzer AI - UI/UX Issues & Tasks

This file tracks all identified bugs, inconsistencies, and improvements.

---

## 🟡 Medium Priority

### 1. Dashboard Missing Pagination
**File:** `users/dashboard.html`
**Problem:** All quizzes are shown in a single grid. Heavy users could have 100+ quizzes.
**Status:** ✅ Fixed - Added pagination with page controls.

### 2. Signup Password Helper Text Always Hidden
**File:** `users/signup.html` line 39
**Problem:** Help text only shows on focus, but validation rules are important upfront.
**Fix:** Consider always-visible password requirements or show on first interaction.

### 3. Dashboard Stats Could Show More Data
**File:** `users/dashboard.html`
**Problem:** Only shows "Total Quizzes" and "Average Score".
**Suggestion:** Add "Best Score", "Total Questions Answered", "Streak".

### 4. No Skip Confirmation
**File:** `quizzes/partials/question_card.html` line 32
**Problem:** Skip button immediately skips with no confirmation.
**Suggestion:** Optional "Are you sure?" for users who might click accidentally.

### 5. Language Grid Could Use Search/Filter
**File:** `core/languages.html`
**Problem:** As more languages are added, browsing becomes slower.
**Suggestion:** Add search bar or category filters.

---

## 🟢 Low Priority / Polish

### 6. CSS `!important` Usage
**File:** `quizzes/partials/question_card.html` lines 154-161
**Problem:** Multiple `!important` declarations are code smell.
**Fix:** Increase selector specificity instead.

### 7. Inline Styles Over CSS Classes
**Files:** Multiple templates
**Problem:** Heavy inline style usage makes global theming difficult.
**Fix:** Extract common patterns to `.btn-*`, `.section-header`, etc.

---

## ✅ Recently Fixed (v1.1.1)

### Code Review Fixes
- [x] **Theme Flash Fix** - Inline script applies theme before Alpine.js loads
- [x] **Slider Theme Fix** - Toggle uses theme-aware CSS variables
- [x] **Dropdown Styling** - Theme-aware hover states, SVG arrows on selects
- [x] **Viewport Protection** - All UI elements constrained to viewport
- [x] **Type Comparison Fix** - Option matching now normalizes to strings
- [x] **Removed `is_study_mode`** - Cleaned up stale model field

---

## ✅ Fixed (v1.1.0)

### Features
- [x] **Dark/Light Theme Toggle** - Sun/moon button with localStorage persistence
- [x] **Toast Notifications** - Slide-in toasts for all user feedback
- [x] **Skeleton Loaders** - Shimmer animations for loading states
- [x] **Mobile Optimization** - Responsive breakpoints, 44px touch targets
- [x] **Accessibility** - Skip link, focus-visible, ARIA labels, reduced motion
- [x] **Timer Per Question** - Live timer with results analytics
- [x] **Structured Logging** - Console and file logging with timing
- [x] **Unit Tests** - pytest with 14 tests passing

### Previous Fixes (v1.0.0)
- [x] Settings Page Shows Email Field
- [x] Logout Link Needs POST Form
- [x] Hardcoded Prism Language Class
- [x] Rate limiting on AI endpoints
- [x] Async AI methods added
- [x] POST requirement on logout
- [x] Email removed from UserUpdateForm
- [x] SECRET_KEY fallback secured
- [x] .gitignore formatting fixed
- [x] SRI on CDN scripts
- [x] N+1 query fixed
- [x] Database indexes added
- [x] code_snippet in chat agent
- [x] Rate limit error handler with friendly message
- [x] Chat input disabled during HTMX request
- [x] Language card active/click feedback
- [x] Standardized `.card-interactive` CSS class
- [x] SEO meta description and Open Graph tags
- [x] Exit quiz button with confirmation modal
- [x] 100% score celebration with emoji 🎉
- [x] Keyboard navigation (1-4 keys + Enter)
- [x] Mobile-responsive chat chips (horizontal scroll)
- [x] Dark mode favicon support
- [x] Dashboard pagination

---

## 🔮 Future Ideas

- [ ] Confetti animation on 100% score
- [ ] PWA support with service worker
- [ ] Leaderboards
- [ ] Export results as PDF
- [ ] Daily streaks gamification
- [ ] E2E tests with Playwright
