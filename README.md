<p align="center">
  <img src="qtrmrs/static/assets/qtrmrs.png" alt="Quizzer AI Logo" width="120"/>
</p>

<h1 align="center"><a href="https://qtrmrs.onrender.com">Quizzer AI</a></h1>

<p align="center">
  Master Coding Interactively with Google Gemini AI
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-green?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/AI-Gemini_Flash-blue?logo=google-gemini" alt="Gemini">
  <img src="https://img.shields.io/badge/License-TSL-red" alt="License">
</p>

> [!NOTE]
> **Personal Project** 🎯 I built this to explore the synergy between Django's robust backend and AI-driven generative logic, specifically focusing on how Gemini can be used to create personalized learning paths for developers.

---

## Live Website 

**➡️ [https://qtrmrs.onrender.com](https://qtrmrs.onrender.com)**

> **Live Demo Limitations**: Render's free tier spins down after inactivity. You may need to wait up to **60 seconds** for the application to wake up. Additionally, memory limits on the free tier may occasionally cause unexpected behavior during heavy AI processing.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Quiz Generation** | Infinite, customized quizzes on any programming topic generated live. |
| � **Immersive Player** | Full-screen interactive interface powered by HTMX and Alpine.js. |
| 🏆 **Gamification** | Earn XP, level up, and unlock achievements as you master new skills. |
| � **Smart Explanations** | Context-aware AI analysis for every mistake you make. |
| 🌙 **Dark/Light Theme** | Professional "Midnight" aesthetic with persistent user preference. |

---

## 🚀 Quick Start

```bash
# Clone and navigate
git clone https://github.com/qtremors/quizzer-ai.git
cd quizzer-ai

# Setup environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Install and run (from qtrmrs folder)
cd qtrmrs
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

---

## 🎮 Demo

### Test Credentials
| Type | Value |
|------|-------|
| Admin Email | `admin@example.com` |
| Password | `password123` |

> These credentials only exist if `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` env vars were set during `build.sh`.

---

## �️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.2.8, Python 3.11+ |
| **AI Engine** | Google Generative AI (Gemini Flash/Pro) |
| **Frontend** | HTMX, Alpine.js, Vanilla CSS |
| **Database** | SQLite (Dev), PostgreSQL (Prod) |

---

## 📁 Project Structure

```
quizzer-ai/
├── .env.example              # Environment template
├── build.sh                  # Render deployment script
├── CHANGELOG.md              # Version history
├── DEVELOPMENT.md            # Architecture & Setup details
├── LICENSE.md                # License terms (TSL)
├── README.md                 # This file
├── TASKS.md                  # Known issues & roadmap
└── qtrmrs/                   # Django project
    ├── pyproject.toml        # Python dependencies
    ├── apps/                 # Modular domain logic
    │   ├── ai_agent/         # AI Service layer
    │   ├── core/             # Landing pages & layout
    │   ├── quizzes/          # Core Quiz domain
    │   └── users/            # Auth & Gamification
    ├── config/               # Settings & URL config
    ├── static/               # Assets, CSS, and JS
    └── templates/            # Django templates
```

---

## � System Resource usage and impact

| Metric | Estimated Usage |
|--------|-----------------|
| **CPU** | Low (Server-side rendering) |
| **RAM** | ~150MB (Django Process) |
| **Disk** | ~20MB (Excl. Venv/DB) |

---

## 🧪 Testing

```bash
cd qtrmrs
uv run pytest -v
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Architecture, Models, and Service logic |
| [CHANGELOG.md](CHANGELOG.md) | Release history and bug fixes |
| [LICENSE.md](LICENSE.md) | Tremors Source License (TSL) |

---

## 📄 License

**Tremors Source License (TSL)** - Source-available license allowing viewing, forking, and derivative works with **mandatory attribution**. Commercial use requires written permission.

See [LICENSE.md](LICENSE.md) for full terms.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/qtremors">Tremors</a>
</p>