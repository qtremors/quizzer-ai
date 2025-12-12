# Quizzer AI - UI/UX Issues & Tasks

This file tracks all identified bugs, inconsistencies, and improvements.

---

## 🟡 Medium Priority

### 1. Dashboard Missing Pagination (Formerly #6)
**File:** `users/dashboard.html`
**Problem:** All quizzes are shown in a single grid. Heavy users could have 100+ quizzes.
**Fix:** Add pagination (10-20 per page) with load more or page controls.

### 2. Signup Password Helper Text Always Hidden (Formerly #11)
**File:** `users/signup.html` line 39
**Problem:** Help text only shows on focus, but validation rules are important upfront.
**Fix:** Consider always-visible password requirements or show on first interaction.

### 3. Dashboard Stats Could Show More Data (Formerly #12)
**File:** `users/dashboard.html`
**Problem:** Only shows "Total Quizzes" and "Average Score".
**Suggestion:** Add "Best Score", "Total Questions Answered", "Streak".

### 4. No Skip Confirmation (Formerly #14)
**File:** `quizzes/partials/question_card.html` line 32
**Problem:** Skip button immediately skips with no confirmation.
**Suggestion:** Optional "Are you sure?" for users who might click accidentally.

### 5. Language Grid Could Use Search/Filter (Formerly #19)
**File:** `core/languages.html`
**Problem:** As more languages are added, browsing becomes slower.
**Suggestion:** Add search bar or category filters.

---

## 🟢 Low Priority / Polish

### 6. CSS `!important` Usage (Formerly #15)
**File:** `quizzes/partials/question_card.html` lines 154-161
**Problem:** Multiple `!important` declarations are code smell.
**Fix:** Increase selector specificity instead.

### 7. Inline Styles Over CSS Classes (Formerly #16)
**Files:** Multiple templates
**Problem:** Heavy inline style usage makes global theming difficult.
**Fix:** Extract common patterns to `.btn-*`, `.section-header`, etc.

---

## ✅ Recently Fixed

- [x] Settings Page Shows Email Field (Fixed)
- [x] Logout Link Needs POST Form (Fixed)
- [x] Hardcoded Prism Language Class (Fixed)
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
