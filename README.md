# 63-45

Dashboard-first personal portfolio operating system for a personal systematic "mini hedge fund".

## Current status

Completed through:

- Step 1: repo bootstrap
- Step 2: database foundation
- Step 3: seed mock portfolio data
- Step 4: portfolio calculation layer
- Step 5: backend API layer
- Step 6: frontend API integration + real Overview page
- Step 7: real Holdings page UI
- Step 8: Allocation page UI
- Step 9: Sync / Data Health page UI

Current working features:

- FastAPI backend
- SQLite database + Alembic migrations
- seeded portfolio snapshot data
- valuation / exposure / concentration services
- sync / health service
- API endpoints for overview, holdings, allocation, and sync status
- React frontend pages for Overview, Holdings, Allocation, and Sync / Health

## Stack

- Backend: FastAPI
- ORM: SQLAlchemy
- Migrations: Alembic
- Database: SQLite
- Frontend: React + TypeScript + Vite
- Data fetching: TanStack Query
- Charts: Recharts

## Base currency

- USD

## Run backend

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```
