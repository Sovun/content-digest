# Content Digest — Product Overview

## Goal

You paste a link to an article → the app extracts the text → AI produces a short
summary, key points, and tags, and **suggests a category** → the result lands as a
**card on a topic-sectioned board**.

## Primary user / context

A reader who saves more articles than they can keep up with, and wants each one
distilled and self-organizing rather than piling up in a read-later list.

## Features

1. **Article ingestion from a URL** — paste a link; the app fetches the page and
   extracts the readable article text (title + body), stripping navigation, ads, and
   boilerplate.
2. **AI digest** — for the extracted text, generate a short summary, the key points,
   and a set of tags.
3. **Category suggestion** — propose a single category for the article (user can
   accept or override).
4. **Topic board** — each processed article becomes a card placed on a board whose
   sections are organized by topic/category.

## Success criteria

- Pasting a valid article URL yields a card with a non-empty summary, key points,
  tags, and a suggested category, with no manual text entry.
- Cards are grouped on the board under the section matching their category.
- A user can override the suggested category and the card moves to the right section.

## Out of scope (initial)

- Accounts, auth, multi-user sync.
- Full-text search across saved articles.
- Mobile-native apps (web only).
- Editing the source article text.

## Architectural decisions

- **Persistence** — board and cards are stored in **Postgres**, accessed via the backend.
  See [ADR 001](../decisions/001-persistence-postgres.md). This confirms a backend is
  required (front-end-only is off the table).
- **Text extraction** — a **lightweight self-hosted Python library** in the backend
  (`trafilatura`, or `readability-lxml` + `httpx`), no headless browser or hosted API.
  See [ADR 002](../decisions/002-text-extraction.md). Unextractable pages surface a clear
  error and create no card.
- **LLM integration** — **OpenRouter** (OpenAI-compatible API) called from the backend,
  producing `{summary, keyPoints, tags, category}` as JSON; model id is config; key read
  from `OPENROUTER_API_KEY`. See [ADR 003](../decisions/003-llm-integration.md).

All architectural questions are resolved; remaining detail (schemas, prompts) is settled
at spec time per feature.
