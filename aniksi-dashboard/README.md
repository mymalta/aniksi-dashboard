# Aniksi Workload Dashboard

A real-time agent workload monitoring dashboard built with FastAPI, Next.js, PostgreSQL, and Redis.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, Tailwind CSS, TypeScript |
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL 16 |
| Cache / Pub-Sub | Redis 7 |
| Containerisation | Docker Compose |

## Features

- Live overview panel with real-time metrics
- Agent board showing individual agent status and workload
- Pressure scoring engine with configurable rules
- Recommendations panel driven by workload analysis
- WebSocket endpoint for live dashboard updates

## Project Structure

```
aniksi-dashboard/
├── backend/
│   ├── app/
│   │   ├── db/          # Database and Redis connections
│   │   ├── engine/      # Pressure, rules, and workload logic
│   │   ├── models/      # SQLAlchemy ORM models
│   │   ├── routers/     # API routes (dashboard, agents, websocket)
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Engine loop and state management
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/         # Next.js app router
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom React hooks
│   │   └── types/       # TypeScript types
│   └── Dockerfile
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Run with Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Run locally (development)

**Backend**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://aniksi:aniksi@postgres:5432/aniksi_dashboard` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379` | Redis connection string |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000` | Backend WebSocket base URL |
