# AI-First CRM HCP Module

An AI-first Healthcare Professional (HCP) CRM module focused on the **Log Interaction** screen. The app supports structured form logging and conversational chat logging, with a FastAPI backend, Redux-powered React frontend, LangGraph agent tools, Groq LLM integration, and SQL persistence.

## Features

- Log HCP interactions from a structured form or an AI chat assistant
- LangGraph agent with five sales tools:
  - `log_interaction`
  - `edit_interaction`
  - `suggest_follow_up`
  - `recommend_materials`
  - `analyze_hcp_sentiment`
- Groq LLM integration with a local deterministic fallback
- SQLAlchemy database layer for SQLite, Postgres, or MySQL
- Interaction history and AI recommendations

## Project Structure

```text
backend/
  app/
    agent/          LangGraph workflow and sales tools
    api/            FastAPI routers
    db/             SQLAlchemy session setup
    models/         Database models
    schemas/        Pydantic schemas
    services/       LLM client and business services
frontend/
  src/
    app/            Redux store
    components/     UI components
    features/       Redux slices
    services/       API client
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

For Groq, set `GROQ_API_KEY` in `backend/.env`. The default model is `openai/gpt-oss-20b`.

The assignment document names `gemma2-9b-it`, but Groq has decommissioned that model. This project keeps the Groq requirement and uses a currently supported Groq-hosted model instead.

Database examples:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/hcp_crm
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hcp_crm
```

If `DATABASE_URL` is omitted, the backend uses local SQLite at `backend/hcp_crm.db`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000`. Override with:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Demo Flow

1. Start the backend.
2. Start the frontend.
3. Use the structured form to log an HCP interaction.
4. Use the AI assistant chat with prompts such as:
   - `Log meeting with Dr. Sharma about Product X efficacy. Positive sentiment. Shared brochure. Follow up in 2 weeks.`
   - `Suggest follow-up for interaction 1`
   - `Recommend materials for cardiology and hypertension`
   - `Analyze sentiment: Doctor was neutral but asked for more safety evidence`
   - `Edit interaction 1 sentiment positive outcome Doctor agreed to formulary discussion`

## Assignment Notes

The provided document requires React, Redux, FastAPI, LangGraph, Groq, SQL storage, and the Inter font. The Google Drive video link in the assignment returned an HTML access/download page in this environment, so this implementation follows the written task and embedded screen mockup.
"# ai-crm-hcp-module" 
