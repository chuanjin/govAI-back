# 🇸🇪 GovAssist AI — Backend

> AI-powered assistant helping users navigate Swedish government services in English, Swedish, and Chinese.

This repository contains the backend service for GovAssist AI, providing a FastAPI-based RAG (Retrieval-Augmented Generation) pipeline integrated with Qdrant vector database and any LLM supported by OpenRouter (e.g., Claude, Mistral, GPT).

---

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern Web Framework.
- **[OpenRouter](https://openrouter.ai/)**: Unified LLM gateway for Claude, GPT, Mistral, etc.
- **[Qdrant](https://qdrant.tech/)**: Vector Database for high-performance RAG.
- **[FastEmbed](https://qdrant.github.io/fastembed/)**: Light-weight, high-speed Python library for generating embeddings.
- **[uv](https://github.com/astral-sh/uv)**: Extremely fast Python package installer and resolver.

---

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.11+** (managed via `uv`)
- **Docker** (to run Qdrant)
- **OpenRouter API Key** (for LLM access)

### 🛠️ 1. Setup Environment
This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

```bash
# 1. Clone & copy environment variables
cp .env.example .env

# 2. Edit .env with your OPENROUTER_API_KEY and other settings
# Suggested model: microsoft/phi-3-mini-128k-instruct:free or anthropic/claude-3-haiku

# 3. Sync project dependencies and virtual environment
uv sync
```

### 🗄️ 2. Start Services
```bash
# Start Qdrant vector database
docker compose up -d

# Seed the database with government documents from /data
uv run scripts/seed_vectordb.py
```

### ⚡ 3. Start API
```bash
# Run with auto-reload during development
uv run uvicorn govai.main:app --reload --port 8000
```
API Documentation will be available at: http://localhost:8000/docs

---

## 🏗️ Architecture

The project is structured as a modern Python package:

```text
├── govai/               # Core package
│   ├── main.py          # FastAPI entrypoint
│   ├── config.py        # Settings via Pydantic
│   ├── models/          # Pydantic schemas
│   ├── routers/         # API endpoints
│   └── services/        # Business logic (LLM, RAG, etc.)
├── data/                # Government service documents (Markdown)
├── scripts/             # Utility scripts (Seeding, Search)
├── tests/               # Project test suite
├── pyproject.toml       # UV project configuration
└── .env                 # Local environment variables (private)
```

---

## ✨ Features (MVP)
- **💬 Natural language chat interface** with context-aware responses.
- **🔍 RAG-based answers** retrieved from official Swedish government data.
- **📋 Structured answers** providing summaries, eligibility, and step-by-step instructions.
- **🌍 Multilingual support** for English, Swedish, and Chinese.
- **🔗 Source attribution** including direct links to government agencies (Skatteverket, CSN, etc.).
- **🎯 Guidance Mode** for walk-through help on complex processes.

---

## 🤝 Development workflow
To add new dependencies:
```bash
uv add [package_name]
```

To run tests:
```bash
uv run pytest
```

---
*Note: For the frontend, please refer to the [govAI-front](https://github.com/cj/repo/govAI-front) repository.*
