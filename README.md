# Project Aether — Akari 🌟

**A modern personal AI companion** built with **React + FastAPI**.

Akari (灯) is designed to be a warm, graceful, and slightly playful companion — not a generic chatbot.

---

## Current Status (Sep 2026)

| Area | Status |
|------|--------|
| Backend (Core Brain) | ✅ Working |
| Frontend (Chat UI) | ✅ Working |
| Long-term Memory | 🔄 Early stage (MongoDB) |
| 3D Model (Blender) | 🔄 Head stage + references |
| Voice | ❌ Not started |
| 3D in App | ❌ Not started |

---

## Features

### Backend
- FastAPI server
- Groq LLM integration
- Akari personality system prompt
- Conversation history (limited to last 10 messages)
- Emotion detection (basic)
- Clear history endpoint
- Early long-term memory (name, goals, plans, preferences)
- Memory injected into AI replies

### Frontend
- React + TypeScript + Vite
- Chat UI with user / Akari bubbles
- Send + Enter to send
- Loading state (“Akari is thinking…”)
- Reset chat (frontend + backend)
- Auto-growing input
- Clean dark + cream theme

### Blender
- Character measurements locked (Marin-based proportions)
- Multi-view reference images
- Outfit inspiration references
- Early head `.blend` files
- Planned: full body → clothing → web export

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite |
| Backend | FastAPI, Python |
| AI | Groq |
| Memory | MongoDB |
| 3D | Blender |
| Future | Three.js / React Three Fiber (planned) |

---

## Project Structure

```text
project-Aether-js/
├── backend/
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── schemas/
│       └── services/      # ai, memory, memory_extractor
├── frontend/
│   └── src/
│       └── App.tsx
├── Blender/
│   ├── references/
│   ├── Akari_model/
│   └── textures/
├── PROJECT_STRUCTURE.md
└── README.md