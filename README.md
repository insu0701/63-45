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

Current working features:

- FastAPI backend
- SQLite database + Alembic migrations
- seeded portfolio snapshot data
- valuation / exposure / concentration services
- API endpoints for overview, holdings, allocation
- React frontend Overview page rendering live backend data

## Stack

- Backend: FastAPI
- ORM: SQLAlchemy
- Migrations: Alembic
- Database: SQLite
- Frontend: React + TypeScript + Vite
- Data fetching: TanStack Query
- Tables: TanStack Table
- Charts: Recharts

## Base currency

- USD

## Run backend

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```
