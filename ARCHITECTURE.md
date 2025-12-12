# Development Plan & Architecture

This document outlines the architectural decisions, development phases, and future roadmap for **Quizzer AI**.

## 1. Architectural Philosophy

We moved away from a monolithic "spaghetti code" structure to a **Service-Oriented Django Architecture**.

- **Hybrid Logic:** Core business logic (quizzes, scoring) lives in `views.py` for simplicity and direct HTMX integration.
    
- **HTMX-First:** We avoid the complexity of a separate React frontend by using Django templates served via HTMX. This allows for SPA-like speed with SEO-friendly HTML.
    
- **AI-as-a-Service:** The AI integration is isolated in `apps/ai_agent/services.py`. The rest of the app doesn't know _how_ the quiz is generated, only that it receives JSON data.
    

## 2. Directory Structure

```
quizzer-ai/
├── qtrmrs/
│   ├── apps/                 # Modular Domains
│   │   ├── ai_agent/         # Gemini Client & Prompt Engineering
│   │   ├── core/             # Landing pages & layout
│   │   ├── quizzes/          # Main Business Logic (Models & Views)
│   │   └── users/            # Custom Auth & Profiles
│   ├── config/               # Settings (Split into base/local/prod)
│   ├── static/               # CSS/JS/Images
│   └── templates/            # HTML (organized by app)
```

## 3. Development Phases (Completed)

### Phase 1: The Foundation (Completed)

- [x] Setup Django 5.x with `uv` package manager.
    
- [x] Refactor folder structure to `apps/` pattern.
    
- [x] Implement Modular Settings (`base.py`, `local.py`).
    
- [x] Create Custom User Model (`AbstractUser` with email login).
    

### Phase 2: The Data Layer (Completed)

- [x] Design Relational Schema: `Quiz` -> `Question` -> `Option` -> `UserAnswer`.
    
- [x] Implement `QuizAttempt` tracking for history.
    
- [x] Add `code_snippet` fields to support technical questions.
    

### Phase 3: The AI Service (Completed)

- [x] Integrate `google-generativeai` SDK.
    
- [x] Design `prompts.py` with strict JSON output enforcement.
    
- [x] Implement `QuizGenerator` service with error handling.
    
- [x] Switch model to `gemini-flash-lite-latest` for speed.
    

### Phase 4: The Frontend System (Completed)

- [x] Build Base Template with HTMX & Alpine.js integration.
    
- [x] Design "Midnight" Theme (Dark Mode by default).
    
- [x] Create responsive Grid layouts for Dashboard and Catalog.
    

### Phase 5: The Interactive Player (Completed)

- [x] Build "Question Card" partials for HTMX swapping.
    
- [x] Implement "Split View" for coding questions (Code left, Options right).
    
- [x] Integrate Prism.js for syntax highlighting.
    
- [x] Create "Explain All Mistakes" logic for bulk AI analysis on results.
    

### Phase 6: The Chat Agent (Completed)

- [x] Build Natural Language Processing (NLP) prompt to extract intent.
    
- [x] Create Chat UI with "Thinking" states and suggestions.
    

### Phase 7: User Experience Polish (Completed)

- [x] **Smart Setup:** Auto-fill Language based on referer URL.
    
- [x] **Feedback:** Loading spinners on all buttons (HTMX indicators).
    
- [x] **Profile:** Avatar uploads and Settings management.
    

## 4. Future Roadmap

### Short Term (In Progress)

- **Leaderboards:** Global ranking based on total score/quizzes taken.
    
- **Export:** Allow users to download their quiz results as PDF.
    
- **Daily Streaks:** Gamification to encourage daily practice.
    

### Long Term

- **Multiplayer:** Real-time quiz battles using Django Channels (WebSockets).
    
- **Resume Analysis:** Upload a resume, generate questions based on listed skills.
    
- **Voice Mode:** Use Gemini's multimodal capabilities for oral technical interviews.