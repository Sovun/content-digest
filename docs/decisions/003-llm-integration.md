# ADR 003 — LLM integration via the Claude API (Anthropic SDK)

## Status

Accepted

## Context

Content Digest's core step turns extracted article text into a short summary, key
points, tags, and a suggested category (see [PRD](../PRD.md), Features 2–3). This needs
an LLM, called from the backend (we already run one — see
[ADR 001](001-persistence-postgres.md) and [ADR 002](002-text-extraction.md)).

"Use Claude Code" was considered and rejected: Claude Code is an interactive developer
*agent* (CLI/IDE tool), not a runtime API an app embeds. The right surface is the
**Claude API** via the official Anthropic SDK.

## Decision

Call the **Claude API** from the Node backend using **`@anthropic-ai/sdk`** (TypeScript).

- **Model:** `claude-opus-4-8` by default. Revisit `claude-sonnet-4-6` later if
  per-article cost matters at volume — not a launch concern.
- **Structured output:** one call per article using structured outputs
  (`output_config.format` / `messages.parse()`) with a JSON schema that forces exactly
  `{ summary, keyPoints[], tags[], category }`. No fragile prose parsing.
- **Auth:** the API key is read from the **`ANTHROPIC_API_KEY`** environment variable at
  runtime. It lives in a local, gitignored `.env` — never committed, never hard-coded.
- The digest call happens server-side after extraction; the result is persisted as a card
  in Postgres.

## Consequences

- **Good:** schema-validated output maps 1:1 to the card model; one well-scoped call per
  article; key stays out of the repo and the browser.
- **Cost:** per-article API cost (mitigable by switching to Sonnet); requires the user to
  provision their own `ANTHROPIC_API_KEY`.
- **Failure handling:** a refusal/over-limit/empty response is treated like an extraction
  failure — clear error, no card (per PRD).

## Open follow-ups

- Exact JSON schema for the digest (field types, tag count bounds) — settle in the
  digest module spec.
- Prompt design for category suggestion (fixed taxonomy vs free-form) — spec-time.
