# Content Digest — Build Plan

> **Stack note:** This plan reflects the chosen MVP stack and is consistent with all three
> decisions: [ADR 001](decisions/001-persistence-postgres.md) (Postgres),
> [ADR 002](decisions/002-text-extraction.md) (Python extraction), and
> [ADR 003](decisions/003-llm-integration.md) (OpenRouter). The product scope in
> [PRD.md](PRD.md) is unchanged.

## Stack

- **Frontend** — Vite + React + TypeScript (static build).
- **Backend** — a minimal **Python FastAPI** service under `/api`, deployed as Vercel
  serverless functions.
- **Storage** — **Postgres** (e.g. Vercel Postgres / Neon) via `DATABASE_URL`.
- **AI** — **OpenRouter** (OpenAI-compatible API) for the summary/points/tags/category
  call, via `OPENROUTER_API_KEY`.
- **Extraction** — Python `trafilatura` (or `readability-lxml` + `httpx`) inside the
  FastAPI service.
- **Host** — Vercel serves the static frontend and routes `/api/*` to FastAPI.

Secrets (`OPENROUTER_API_KEY`, `DATABASE_URL`) live in Vercel env vars and a local,
gitignored `.env` — never committed.

## Folder structure

```
content-digest/
├── api/
│   ├── index.py            # FastAPI ASGI app — Vercel serves /api/* from here
│   ├── digest.py           # fetch URL → extract text → OpenRouter → structured digest
│   ├── db.py               # Postgres connection + card queries
│   └── requirements.txt    # fastapi, httpx, trafilatura, psycopg[binary]
├── src/                    # Vite + React + TS frontend
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/         # UrlInput, Board, Card, Section
│   └── lib/api.ts          # fetch wrappers to /api
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── vercel.json             # static build + Python function routing
├── .env.example            # OPENROUTER_API_KEY, DATABASE_URL
└── docs/                   # PRD, PLAN, decisions
```

## Build steps (empty → MVP)

1. **Scaffold & wire hosting.** `npm create vite@latest` (react-ts) at the root; add
   `api/index.py` with a FastAPI `GET /api/health`; add `vercel.json` routing static →
   frontend and `/api/*` → the Python function; add `.env.example`. Verify the dev
   frontend and the health endpoint both respond.
2. **Postgres + schema.** Provision a Postgres database, set `DATABASE_URL`, and create
   the `cards` table (`id, url, title, summary, key_points jsonb, tags jsonb, category,
   created_at`) in `db.py`. Add `GET /api/cards` returning all cards.
3. **Ingest pipeline.** Implement `POST /api/cards` in `digest.py`: fetch the URL,
   extract readable text with `trafilatura`, call OpenRouter for a JSON digest
   `{summary, key_points, tags, category}`, persist a card, return it. Unextractable
   URLs → clear error, no card.
4. **Frontend board.** Build the paste-a-URL input that calls `POST /api/cards`, then a
   topic-sectioned board (`Board` → `Section` → `Card`) reading from `GET /api/cards`;
   group cards by `category` and allow overriding it.
5. **Deploy MVP.** Push to Vercel, set `OPENROUTER_API_KEY` + `DATABASE_URL` env vars,
   connect Postgres, and confirm the end-to-end paste → card → board flow in production.
