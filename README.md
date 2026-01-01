# Quizzer AI

**Master Coding Interactively with Google Gemini AI**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.x-green.svg)
![HTMX](https://img.shields.io/badge/htmx-1.9-orange.svg)
![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen.svg)

Quizzer AI is a modern, adaptive learning platform designed for developers. It leverages **Google's Gemini AI** models to generate infinite, customized quizzes on any programming topic—from Python syntax to System Design architecture.

Unlike static quiz apps, Quizzer AI generates fresh content on the fly, analyzes your answers, and provides context-aware explanations for every mistake you make.

---

## ✨ Key Features

### 🧠 AI-Powered Generation
- **Dynamic Content:** No database of pre-written questions. Every quiz is generated live based on your specific request (Topic, Difficulty, Language).
- **Natural Language Agent:** Chat directly with the AI (e.g., _"Give me a hard quiz on React Hooks optimization"_) to generate a session.
- **Coding Challenges:** Supports code-based questions with a split-screen syntax highlighter (Prism.js) for realistic debugging scenarios.
- **Multiple AI Models:** Choose from Gemini Flash, Flash Lite, Pro, and more.

### 🎮 Immersive Player
- **Distraction-Free UI:** A full-screen, focused interface designed for deep work.
- **Adaptive Layout:** Automatically switches between text-only and split-code layouts based on the question type.
- **Instant Interactions:** Powered by **HTMX** for a smooth, single-page-app feel without page reloads.
- **⏱️ Timer Per Question:** Track time spent on each question with live display and results analytics.

### 📊 Analytics & Growth
- **Smart Explanations:** Don't just see _what_ is wrong, understand _why_. Click "Explain All Mistakes" to get an AI breakdown of your specific logic errors.
- **History Tracking:** A dashboard that tracks every attempt, score, and topic mastery over time.
- **Time Analytics:** See total quiz time and average time per question on results.
- **Persistent Storage:** All AI-generated explanations are cached to save API costs and provide instant retrieval later.

### 🎨 Modern UI/UX
- **🌙 Dark/Light Theme:** Toggle between themes with persistent preference.
- **🔔 Toast Notifications:** Beautiful slide-in notifications for all actions.
- **📱 Mobile Optimized:** Responsive design with proper touch targets.
- **♿ Accessible:** Skip links, focus management, screen reader support, reduced motion.
- **⏳ Skeleton Loaders:** Smooth loading states with shimmer animations.

---

## 🏗️ Tech Stack

- **Backend:** Django 5.2 (Python 3.11+)
- **AI Engine:** Google Generative AI SDK (Gemini Flash/Pro)
- **Frontend:**
    - **HTMX:** For server-side reactivity and AJAX navigation.
    - **Alpine.js:** For client-side interactions (modals, dropdowns, theme toggle).
    - **CSS:** Custom CSS Variables (Theming) & Flex/Grid layouts.
- **Database:** SQLite (Dev) / PostgreSQL Ready (Prod)
- **Testing:** pytest + pytest-django + pytest-cov
- **Utilities:** Prism.js (Syntax Highlighting), Devicon (Logos).

---

## 🚀 Getting Started

Follow these instructions to set up the project on your local machine.

### Prerequisites

- **Python 3.11+** installed.
- **uv** package manager installed (`pip install uv`).
- **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/qtremors/quizzer-ai.git
   cd quizzer-ai
   ```

2. **Install Dependencies with uv:**
   This project uses `uv` for blazing fast package management.
   ```bash
   # Install uv if you don't have it
   pip install uv
   
   # Sync dependencies (creates .venv automatically)
   uv sync
   
   # For development (includes testing tools)
   uv pip install -e ".[dev]"
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   # .env
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_django_secret_key  # Optional for local dev
   DEBUG=True
   ```

4. **Initialize Database:**
   ```bash
   cd qtrmrs
   uv run python manage.py migrate
   ```

5. **Create Admin User:**
   ```bash
   uv run python manage.py createsuperuser
   ```

### Running the Application

Start the development server:

```bash
uv run python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

---

## 🧪 Testing

Run the test suite:

```bash
cd qtrmrs
uv run pytest -v
```

Run with coverage:

```bash
uv run pytest --cov=apps --cov-report=html
```

---

## 📂 Architecture

The project follows a **Domain-Driven Design** (DDD) within Django, avoiding the default flat structure:

- `apps/core`: Global pages (Home, Language Catalog) and shared templates.
- `apps/users`: Custom Authentication, Profile Management, and Dashboards.
- `apps/quizzes`: The core domain logic (Quiz generation, Question storage, Attempt tracking) via **Hybrid Views**.
- `apps/ai_agent`: Isolated **Service Layer** (`services.py`) for communicating with Google Gemini.

### Key Directories

```
quizzer-ai/
├── qtrmrs/
│   ├── apps/                 # Modular Domains
│   │   ├── ai_agent/         # Gemini Client & Prompt Engineering
│   │   ├── core/             # Landing pages & layout
│   │   ├── quizzes/          # Main Business Logic
│   │   │   └── tests/        # Unit tests
│   │   └── users/            # Custom Auth & Profiles
│   ├── config/               # Settings (Split into base/local/prod)
│   ├── static/               # CSS/JS/Images
│   │   ├── css/
│   │   │   ├── theme.css     # Theme variables
│   │   │   ├── base.css      # Core styles + mobile + a11y
│   │   │   ├── toast.css     # Toast notifications
│   │   │   └── skeleton.css  # Loading skeletons
│   │   └── js/
│   │       └── toast.js      # Toast Alpine.js store
│   ├── templates/            # HTML (organized by app)
│   ├── logs/                 # Application logs
│   └── conftest.py           # Pytest fixtures
├── pyproject.toml            # Dependencies & pytest config
└── README.md
```

---

## 🛠️ Management Commands

Standard Django commands:

- **Run Server:** `uv run python manage.py runserver`
- **Run Tests:** `uv run pytest -v`
- **Reset Database:** `uv run python manage.py flush`
- **Check System:** `uv run python manage.py check`
- **Make Migrations:** `uv run python manage.py makemigrations`

---

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.