# 🇸🇪 GovAssist AI — Backend

> AI-powered assistant helping users navigate Swedish government services in English, Swedish, and Chinese.

This repository contains the backend service for GovAssist AI, providing a FastAPI-based RAG (Retrieval-Augmented Generation) pipeline integrated with Qdrant vector database and Gemini models (via LiteLLM).

---

## 🛠️ Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern Web Framework.
- **[Gemini (via LiteLLM)](https://ai.google.dev/)**: Powerful LLM for response generation.
- **[LiteLLM](https://docs.litellm.ai/)**: Simplified LLM interaction and fallbacks.
- **[Qdrant](https://qdrant.tech/)**: Vector Database for high-performance RAG.
- **[FastEmbed](https://qdrant.github.io/fastembed/)**: Light-weight, high-speed Python library for generating embeddings.
- **[uv](https://github.com/astral-sh/uv)**: Extremely fast Python package installer and resolver.

---

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.11+** (managed via `uv`)
- **Docker** (to run Qdrant)
- **Gemini API Key** (for LLM access)

### 🛠️ 1. Setup Environment
This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management or Docker for streamlined containerized setup.

```bash
# 1. Clone & copy environment variables
cp .env.example .env

# 2. Edit .env with your GEMINI_API_KEY and other settings
```

### 🐳 Option A: Using Docker (Recommended)
This starts both the API and the Qdrant database.

```bash
# 1. Build and start services
docker compose up -d

# 2. Seed the database (runs in a ephemeral container)
docker compose run --rm api uv run scripts/seed_vectordb.py
```
API Documentation will be available at: http://localhost:8000/docs

### 🐍 Option B: Local Python Setup
Use this for active development with auto-reload.

```bash
# 1. Sync project dependencies and virtual environment
uv sync

# 2. Start Qdrant vector database
docker compose up qdrant -d

# 3. Seed the database
uv run scripts/seed_vectordb.py

# 4. Start API with auto-reload
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
- **🌍 Multilingual support** with language-aware prompting and multilingual embeddings.
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
