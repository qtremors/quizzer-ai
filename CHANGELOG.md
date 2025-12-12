# Changelog

All notable changes to the **Quizzer AI** project.

## [1.1.0] - 2025-12-12

### 🎨 UI/UX Enhancements

- **Theme Toggle:** Added dark/light theme switcher with localStorage persistence and system preference detection.
- **Toast Notifications:** Implemented slide-in toast notification system with Alpine.js store (success, error, warning, info variants).
- **Skeleton Loaders:** Added shimmer loading animations for improved perceived performance.
- **Mobile Optimization:** Responsive breakpoints at 768px and 480px with proper touch targets (44px minimum).

### ♿ Accessibility

- **Skip to Content:** Added skip link for keyboard navigation.
- **Focus Management:** Implemented `:focus-visible` outlines for better accessibility.
- **ARIA Labels:** Added `role` attributes and screen reader utilities.
- **Reduced Motion:** Support for `prefers-reduced-motion` media query.
- **High Contrast:** Added `prefers-contrast: high` support.

### ⏱️ Quiz Features

- **Timer Per Question:** Live timer display during quizzes with time tracking per answer.
- **Study Mode:** New toggle to show correct answer and explanation immediately after each question.
- **Time Analytics:** Results page now shows total time and average time per question.
- **AI Model Badge:** Display which AI model was used on results page.

### 🔧 Technical Improvements

- **Structured Logging:** Added Django logging configuration with console/file handlers and timing metrics.
- **Unit Tests:** Added pytest + pytest-django setup with 15 initial tests.
- **Test Fixtures:** Created conftest.py with user, quiz, and model fixtures.
- **Error Handling:** Enhanced AIError class with specific error types (quota, auth, timeout, model_not_found).

### 📦 Dependencies

- Added `pytest>=8.0.0`, `pytest-django>=4.7.0`, `pytest-cov>=4.1.0` as dev dependencies.

---

## [1.0.0] - 2025-11-19

### 🚀 Architecture & Core

- **Refactor:** Completely rebuilt the legacy project into a scalable `apps/` based architecture.
- **Settings:** Split configuration into `base.py` (shared) and `local.py` (dev).
- **Auth:** Implemented Custom User Model and secure session handling.


### 🧠 AI & Logic

- **Service Layer:** Created `QuizGenerator` service to abstract Gemini API calls.
- **Reliability:** Implemented JSON enforcement in prompts to prevent parsing errors.
- **Features:** Added support for "Coding Questions" (generating code snippets alongside text).
- **Agent:** Added a Natural Language Parser to convert chat messages (e.g., "Hard Python Quiz") into structured database queries.


### 🎨 UI/UX (The "Midnight" Theme)

- **Design:** Implemented a professional Dark Mode aesthetic using CSS Variables.
- **Layout:**
    - Created a 1600px wide responsive container for Dashboards.
    - Implemented a "Split View" layout for coding challenges (60/40 split).
    - Designed a Sticky Glassmorphism Navbar.
        
- **Interactions:**
    - Added HTMX loading states (spinners) to all major buttons.
    - Implemented Alpine.js dropdowns and form focus effects.
    - Created a seamless "Immersive Mode" for the Quiz Player (no scrolling required).
        

### 📱 Features

- **Dashboard:** Added a grid-based history view with score badges and stats.
- **Language Catalog:** Created a dedicated `/languages` page with Devicon integration.
- **Result Analysis:** Added "Explain All Mistakes" button that batch-processes wrong answers via AI and saves them to the DB.
- **Settings:** Added Profile management (Avatar upload, Username edit) and Password Reset flows.


### 🐛 Bug Fixes

- Fixed `floatform` template error by casting scores to integers in views.
- Fixed Navbar "Clone" bug by using `HX-Redirect` headers for page transitions.
- Fixed "Dots" on radio buttons by using `display: none` on inputs and styling labels.
- Fixed "Edit Button" overlap in settings by using Flexbox gaps.
- Fixed Language Auto-select logic to prioritize Custom Input over Dropdown.