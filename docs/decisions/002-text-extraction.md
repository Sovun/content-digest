# ADR 002 — Extract article text with a lightweight self-hosted library

## Status

Accepted

## Context

Content Digest ingests an article URL and needs the readable title + body, stripped of
nav, ads, and boilerplate, before the AI digest runs. Browser-only fetch hits CORS limits,
and we already run a Node backend (see [ADR 001](001-persistence-sqlite.md)), so extraction
happens server-side.

Options considered:
- **Lightweight self-hosted libs** (`@extractus/article-extractor`, Mozilla Readability +
  `jsdom`) — free, in-process, fast; only see the initial HTML.
- **Headless browser** (Playwright/Puppeteer) — handles JS-rendered pages; heavy binary,
  slow, more infra. Free, but operational cost.
- **Hosted APIs** (Jina Reader, Firecrawl, etc.) — handle the hard cases; external
  dependency, API keys, usage limits.

## Decision

Use a **lightweight self-hosted extraction library** in the backend, fetching HTML via
`undici`. No headless browser, no hosted API for the MVP.

- Primary: `@extractus/article-extractor` (or Mozilla Readability + `jsdom`) — exact pick
  settled in the extraction module's spec.
- Pages that can't be extracted (JS-rendered SPAs, blocked, paywalled) surface a **clear
  error and create no card**, per the PRD.

## Consequences

- **Good:** free, no external dependency, fast, data stays in-house; simplest MVP path.
- **Cost:** only sees the initial HTML — JS-rendered/lazy-loaded articles will fail
  extraction. Accepted for MVP: those become clean errors, not silent bad cards.
- **Migration path:** if the failure rate is too high, add a fallback (Playwright
  self-hosted, or Jina Reader hosted) behind the same extraction interface — own ADR.

## Open follow-ups

- Final library choice between `@extractus/article-extractor` and Readability+`jsdom` —
  settle in the extraction module spec.
