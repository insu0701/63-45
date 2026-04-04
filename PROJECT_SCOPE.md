# PROJECT_SCOPE.md

# Automated Mini Hedge Fund — Project Scope

## 1. Project Purpose

This project builds a personal, systematic, dashboard-first portfolio operating system for a long-only multi-market equity strategy.

The immediate objective is **not** to automate live trading.

The immediate objective is to build a **read-only portfolio review platform** that provides a clean, normalized, customizable view of:

- current holdings
- cash balances
- Korea vs US exposure
- portfolio weights
- unrealized P&L
- concentration
- sync/data health

This dashboard will become the foundation for later phases:

1. real sync workflows
2. strategy overlay
3. shadow-mode signal review
4. assisted-mode order review
5. live automation

---

## 2. v0 Goal

Version 0 (`v0`) is a **read-only portfolio dashboard**.

It must answer:

- What do I currently own?
- How much KRW cash and USD cash do I have?
- How much of my portfolio is in Korea equities vs US equities?
- What is my unrealized P&L?
- What are my largest positions?
- How concentrated is my portfolio?
- When was my data last refreshed?

---

## 3. In Scope for v0

The following are in scope for `v0`:

### 3.1 Portfolio Data Model

- internal normalized portfolio schema
- holdings snapshots
- cash balance snapshots
- price snapshots
- FX snapshots
- sector mappings
- sync logs
- data issue logs

### 3.2 Data Sources

- Korea holdings and balances from Kiwoom (read-only)
- US holdings via manual/CSV import
- FX rates for USD base-currency reporting
- price data sufficient for valuation display

### 3.3 Core Calculations

- total NAV
- KR sleeve value
- US sleeve value
- KRW cash
- USD cash
- cost basis
- market value
- unrealized P&L
- unrealized return %
- position weights
- sleeve weights
- concentration metrics
- country/sector/currency allocation

### 3.4 Backend

- FastAPI application
- SQLite database
- Alembic migrations
- REST API endpoints for overview, holdings, allocation, sync status, and health

### 3.5 Frontend

- React + TypeScript dashboard
- Overview page
- Holdings page
- Allocation page
- Sync / Data Health page

### 3.6 Operational Mode

- local development only
- single-user only
- read-only only

---

## 4. Out of Scope for v0

The following are explicitly out of scope for `v0`:

### 4.1 Trading and Execution

- order placement
- order cancellation
- order modification
- broker write actions
- auto-trading
- live execution workflows

### 4.2 Strategy Logic

- signal generation
- MACD / RSI / confirmation-cross engine
- Morningstar universe automation
- InfoStock universe automation
- target position calculation
- target-vs-actual review
- shadow-mode order generation

### 4.3 Advanced Analytics

- backtesting
- performance attribution
- factor exposure modeling
- tax accounting
- scenario analysis
- PnL decomposition by signal

### 4.4 Product Expansion

- mobile app
- cloud deployment
- multi-user auth
- admin panel
- broker abstraction for multiple live brokers

---

## 5. Technical Decisions Locked in Step 0

The following decisions are fixed for `v0`:

### 5.1 Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic

### 5.2 Database

- SQLite

### 5.3 Frontend

- React
- TypeScript
- Vite

### 5.4 Base Currency

- USD

### 5.5 Primary Broker Assumption

- Kiwoom for Korea holdings sync
- US holdings handled initially through import rather than broker automation

---

## 6. Product Rules for v0

### 6.1 Broker Truth First

The dashboard must reflect actual holdings and balances, not hypothetical strategy positions.

### 6.2 Normalize Before Display

The UI must not depend directly on raw broker payloads.  
All source data must first be normalized into internal portfolio models.

### 6.3 Snapshot-Based Architecture

The system must store historical snapshots rather than only current state.

### 6.4 Read-Only Safety

No trade-capable endpoints or UI controls are permitted in `v0`.

### 6.5 Desktop First

`v0` is optimized for desktop/laptop use only.

---

## 7. v0 Deliverables

`v0` is complete only when all of the following exist:

### 7.1 Working Local App

- backend starts locally
- frontend starts locally
- database initializes successfully

### 7.2 Working Overview

The Overview page displays:

- total NAV
- KR equity value
- US equity value
- KRW cash
- USD cash
- total unrealized P&L
- total unrealized return %
- last refresh time

### 7.3 Working Holdings View

The Holdings page displays:

- Korea holdings
- US holdings
- combined holdings
- per-position values and weights

### 7.4 Working Allocation View

The Allocation page displays:

- sleeve allocation
- country allocation
- sector allocation
- currency allocation

### 7.5 Working Sync / Data Health View

The Sync page displays:

- last successful sync/import
- last failed sync/import
- warnings
- open data issues

---

## 8. Definition of Done for Step 0

Step 0 is complete when:

1. this file exists at repo root as `PROJECT_SCOPE.md`
2. all implementation decisions in Sections 3–5 are accepted as the current project boundary
3. no Sprint 1 task violates this scope
4. the project is explicitly understood to be **dashboard-first, read-only-first**

---

## 9. Planned Phase Order After v0

The intended project order is:

### Phase A

Read-only portfolio dashboard (`v0`)

### Phase B

Real sync workflows

### Phase C

Strategy-overlay-ready schema and UI hooks

### Phase D

Shadow-mode signal engine

### Phase E

Assisted-mode review and proposed orders

### Phase F

Live broker execution automation

This order is intentional.  
The project must not skip directly from `v0` to live auto-trading.

---

## 10. Non-Goals

This project is not trying to be:

- a clone of Hero Moon
- a full institutional OMS/EMS
- a mobile-first investing app
- a broker-agnostic retail platform
- a complete hedge fund infrastructure stack on day one

The project is trying to be:

> a reliable personal portfolio operating system that can later grow into a systematic mini-fund workflow.

---

## 11. Current Implementation Status

As of the latest completed phase, the project has implemented:

- backend bootstrap
- frontend bootstrap
- SQLite schema + Alembic migrations
- seed portfolio data
- valuation / exposure / concentration services
- backend API endpoints for overview, holdings, allocation, and sync status
- frontend pages for Overview, Holdings, Allocation, and Sync / Health

The project remains read-only.  
No broker write actions, order placement, or live trading automation are included in the current implemented scope.
