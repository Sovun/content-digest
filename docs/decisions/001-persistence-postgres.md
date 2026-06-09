# ADR 001 — Persist the board and cards in Postgres

## Status

Accepted

## Context

Content Digest produces cards (summary, key points, tags, category) that live on a
topic-sectioned board. These must persist across sessions. The MVP is single-user
(see [PRD](../PRD.md)) but is deployed on Vercel with serverless functions, so a
managed, network-accessible database is the natural fit.

The backend (a Python FastAPI service — see [ADR 002](002-text-extraction.md)) owns all
database access; the browser never talks to the database directly.

## Decision

Use **Postgres** as the persistence layer for the board and its cards, accessed through
the backend (e.g. Vercel Postgres or Neon, via a `DATABASE_URL` connection string).

- Likely table: `cards` (`id`, `url`, `title`, `summary`, `key_points` JSONB,
  `tags` JSONB, `category`, `created_at`). Sections can be derived from `category` or
  promoted to their own table later — settled in the schema spec.
- The backend exposes the board over an API the React app consumes.

## Consequences

- **Good:** managed and serverless-friendly (no DB process to run ourselves); scales
  beyond single-user without re-platforming; JSONB fits the variable tag/key-point shape;
  works cleanly with Vercel's function model.
- **Cost:** requires provisioning a Postgres instance and managing a `DATABASE_URL`
  secret; a network round-trip per query (vs. an embedded store).
- **Migration path:** the React app talks only to the backend API, so the database can be
  swapped or scaled without front-end changes.

## Open follow-ups

- Postgres driver / access layer choice (e.g. `psycopg`, SQLAlchemy) — own spec/ADR.
- Schema for tags/key points (JSONB column vs child table).
