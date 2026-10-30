# Policy Intel: Deployment Guide

This guide covers deployment instructions for the Policy Intel platform across various production hosting topologies:
- **Backend**: Render / Railway / AWS ECS / Self-Hosted VPS
- **Frontend**: Vercel / Netlify / Cloudflare Pages
- **Database**: Managed PostgreSQL (AWS RDS / Supabase / Neon / Render Postgres)

---

## 1. Environment Variables Configuration

Copy `.env.example` to `.env` in the root and configure:

```bash
# Backend Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=8000

# Database Configuration
# For local evaluation:
DATABASE_URL=sqlite:///./policy_intel.db
# For production PostgreSQL:
# DATABASE_URL=postgresql://user:password@db.example.com:5432/policy_intel

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=https://policy-intel.vercel.app,http://localhost:5173

# Optional LLM API Keys (for extended semantic reasoning)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 2. Backend Deployment (Render / Docker)

### Dockerfile
A production-ready Dockerfile for the backend service:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY intelligence/ ./intelligence/
COPY data/ ./data/
COPY ingestion/ ./ingestion/
COPY backend/ ./backend/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 3. Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel.
2. Set Root Directory: `frontend`.
3. Build Command: `npm run build`.
4. Output Directory: `dist`.
5. Environment Variable:
   - `VITE_API_URL`: URL of your deployed backend (e.g. `https://policy-intel-api.onrender.com`).

---

## 4. Zero-Downtime Resilience & Fallbacks

- **Database Resilience**: The backend automatically falls back to SQLite or in-memory registration if an external PostgreSQL connection fails, guaranteeing that read queries and graph visualizers remain operable.
- **Offline Agent Resilience**: If external LLM API endpoints experience rate limits or network dropouts, the LangGraph agent utilizes deterministic rule-based tool execution, guaranteeing 100% reliable, hallucination-free output.
