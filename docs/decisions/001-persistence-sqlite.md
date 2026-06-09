# ADR 001 — Persist the board and cards in SQLite

## Status

Accepted

## Context

Content Digest produces cards (summary, key points, tags, category) that live on a
topic-sectioned board. These must persist across sessions. The MVP is single-user and
local-first — no accounts, no multi-user sync (see [PRD](../PRD.md)).

Separately, article-text extraction can't run from the browser alone (CORS), so a small
backend is already needed. That backend is the natural home for the database.

## Decision

Use **SQLite** as the persistence layer for the board and its cards, accessed through the
backend process (not from the browser directly).

- One SQLite file holds cards and their board placement.
- Likely tables: `cards` (url, title, summary, key_points, tags, category, created_at) and,
  if sections need to be first-class, `sections` (category/topic). Tags/key points may be
  JSON columns or a child table — to be settled in the schema spec.
- The backend exposes the board over an API the React app consumes.

## Consequences

- **Good:** zero-config, file-based, no DB server to run; fits single-user local-first;
  trivial backups (copy the file); the extraction backend and DB share one process.
- **Cost:** confirms a backend is required — front-end-only is off the table. Concurrency
  and multi-user are not addressed (acceptable: out of MVP scope).
- **Migration path:** if multi-user/sync is ever in scope, swap SQLite for a hosted DB
  behind the same API; the React app shouldn't need to change.

## Open follow-ups

- Backend runtime + SQLite driver choice (e.g. `better-sqlite3`) — own spec/ADR.
- Schema for tags/key points (JSON column vs child table).
