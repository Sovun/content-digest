# ADR 003 — LLM integration via OpenRouter

## Status

Accepted

## Context

Content Digest's core step turns extracted article text into a short summary, key
points, tags, and a suggested category (see [PRD](../PRD.md), Features 2–3). This needs
an LLM, called from the backend — a Python FastAPI service (see
[ADR 001](001-persistence-postgres.md) and [ADR 002](002-text-extraction.md)).

We want one provider that exposes many models behind a single, stable API so the model
choice can change without rewiring the integration.

## Decision

Call the LLM through **OpenRouter** (`https://openrouter.ai`), which offers an
**OpenAI-compatible** API over many models.

- **Client:** any OpenAI-compatible HTTP client from the FastAPI service (e.g. `httpx`,
  or the `openai` SDK pointed at OpenRouter's base URL).
- **Model:** chosen via OpenRouter's model id (e.g. an `anthropic/claude-*` or other
  model); the id is config, so it can be swapped without code changes.
- **Structured output:** one call per article, requesting JSON
  `{ summary, key_points, tags, category }` (JSON mode / response schema where supported,
  otherwise prompt-enforced and validated server-side). No fragile prose parsing.
- **Auth:** the API key is read from the **`OPENROUTER_API_KEY`** environment variable at
  runtime. It lives in a local, gitignored `.env` (and Vercel env vars in production) —
  never committed, never hard-coded.
- The digest call happens server-side after extraction; the result is persisted as a card
  in Postgres.

## Consequences

- **Good:** one integration, many swappable models; provider/model choice is a config
  change; key stays out of the repo and the browser.
- **Cost:** per-article API cost (mitigable by choosing a cheaper model); requires the
  user to provision an `OPENROUTER_API_KEY`; OpenRouter is an extra hop in the path.
- **Failure handling:** a refusal / over-limit / empty / malformed response is treated
  like an extraction failure — clear error, no card (per PRD).

## Open follow-ups

- Exact JSON schema for the digest (field types, tag count bounds) and which model id to
  default to — settle in the digest module spec.
- Prompt design for category suggestion (fixed taxonomy vs free-form) — spec-time.
