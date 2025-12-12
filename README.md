# Quizzer AI

**Master Coding Interactively with Google Gemini AI**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-5.x-green.svg)
![HTMX](https://img.shields.io/badge/htmx-1.9-orange.svg)

Quizzer AI is a modern, adaptive learning platform designed for developers. It leverages **Google's Gemini 2.0 Flash** model to generate infinite, customized quizzes on any programming topic—from Python syntax to System Design architecture.

Unlike static quiz apps, Quizzer AI generates fresh content on the fly, analyzes your answers, and provides context-aware explanations for every mistake you make.

---

## ✨ Key Features

### 🧠 AI-Powered Generation
- **Dynamic Content:** No database of pre-written questions. Every quiz is generated live based on your specific request (Topic, Difficulty, Language).
- **Natural Language Agent:** Chat directly with the AI (e.g., _"Give me a hard quiz on React Hooks optimization"_) to generate a session.
- **Coding Challenges:** Supports code-based questions with a split-screen syntax highlighter (Prism.js) for realistic debugging scenarios.

### 🎮 Immersive Player
- **Distraction-Free UI:** A full-screen, focused interface designed for deep work.
- **Adaptive Layout:** Automatically switches between text-only and split-code layouts based on the question type.
- **Instant Interactions:** Powered by **HTMX** for a smooth, single-page-app feel without page reloads.

### 📊 Analytics & Growth
- **Smart Explanations:** Don't just see _what_ is wrong, understand _why_. Click "Explain All Mistakes" to get an AI breakdown of your specific logic errors.
- **History Tracking:** A dashboard that tracks every attempt, score, and topic mastery over time.
- **Persistent Storage:** All AI-generated explanations are cached to save API costs and provide instant retrieval later.

---

## 🏗️ Tech Stack

- **Backend:** Django 5.2 (Python 3.11+)
- **AI Engine:** Google Generative AI SDK (Gemini 2.0 Flash Lite)
- **Frontend:**
    - **HTMX:** For server-side reactivity and AJAX navigation.
    - **Alpine.js:** For client-side interactions (modals, dropdowns).
    - **CSS:** Custom CSS Variables (Theming) & Flex/Grid layouts.
- **Database:** SQLite (Dev) / PostgreSQL Ready (Prod)
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
   git clone https://github.com/yourusername/quizzer-ai.git
   cd quizzer-ai
   ```

3. **Install Dependencies with uv:**
   This project uses `uv` for blazing fast package management.
   ```bash
   # Install uv if you don't have it
   pip install uv
   
   # Sync dependencies (creates .venv automatically)
   uv sync
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```bash
   # .env
   GEMINI_API_KEY=your_api_key_here
   SECRET_KEY=your_django_secret_key  # Optional for local dev
   DEBUG=True
   ```

5. **Initialize Database:**
   ```bash
   cd qtrmrs
   uv run manage.py migrate
   ```

6. **Create Admin User:**
   ```bash
   uv run manage.py createsuperuser
   ```

### Running the Application

Start the development server:

```bash
uv run manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

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
│   │   └── users/            # Custom Auth & Profiles
│   ├── config/               # Settings (Split into base/local/prod)
│   ├── static/               # CSS/JS/Images
│   └── templates/            # HTML (organized by app)
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Management Commands

We have custom management commands (if applicable) or standard Django commands:

- **Reset Database:** `python manage.py flush`
- **Check System:** `python manage.py check`

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