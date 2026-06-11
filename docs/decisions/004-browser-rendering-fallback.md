# ADR 004 — Browser-rendering fallback with user-supplied cookies

## Status

Accepted — supersedes the "no headless browser" constraint of
[ADR 002](002-text-extraction.md).

## Context

Two classes of articles can't be ingested by the plain `httpx` fetch
([issue #7](https://github.com/Sovun/content-digest/issues/7)):

1. **Bot-blocked sites** — Medium returns HTTP 403 to any non-browser client;
   the detection happens below HTTP (TLS fingerprinting), so no header
   spoofing helps. JS-rendered SPAs similarly yield no extractable text.
2. **Login-gated content** — member-only stories the reader is legitimately
   authorized to see via their own account; an anonymous fetch gets a paywall
   stub.

ADR 002 deliberately excluded a headless browser for the MVP, accepting these
as clean errors, and named a fallback "behind the same extraction interface"
as the migration path. The failure rate on the primary target (Medium) makes
that fallback due now.

Options considered (from the issue):

- **A. User-supplied cookies only** — simple, but does not defeat TLS-level
  bot detection (Medium still 403s anonymously fetched member content).
- **B. Browser extension / bookmarklet posting captured HTML** — works for
  everything, but a bookmarklet POSTing from the article page is blocked by
  strict site CSP (`connect-src`) on exactly the target sites, and a real
  extension is a heavy new artifact.
- **C. Headless browser (Playwright)** — a real Chromium has a real TLS
  fingerprint, so bot detection passes; combined with **A** for login-gated
  pages it covers both failure classes with a URL-only UX.

## Decision

**Automatic browser-rendering fallback (C) plus per-request user cookies (A).**

- The plain `httpx` fetch stays first. Only when it returns **4xx** or the
  fetched HTML yields **no readable text** does the pipeline retry once by
  rendering the page in headless Chromium via **Playwright (sync API)**.
  5xx and network errors stay terminal — a browser wouldn't help.
- **Where the browser runs:** if `BROWSER_WS_ENDPOINT` is set, Playwright
  connects to a remote browser over CDP (Browserless, Browserbase, …) — this
  is the production path, since Vercel functions can't host Chromium
  (250 MB unzipped limit). Unset (the dev path), it prefers a **headed system
  Chrome parked offscreen**: verified empirically, headless Chromium gets an
  unsolvable "security verification" interstitial from Medium while headed
  Chrome passes. If Chrome or a display is missing it falls back to headless
  Playwright Chromium (`playwright install chromium`). One code path,
  selected by env var.
- **Cookies:** the frontend stores per-site cookies the user pastes (Cookie
  header value or cookies.txt) in **localStorage only**, keyed by domain, and
  sends them — with that domain — in the `POST /api/cards` body when the
  article's host matches. The backend scopes them to that domain and its
  subdomains for that single fetch: the httpx path follows redirects manually
  and attaches the `Cookie` header only while the hop stays on the domain
  (httpx strips a manually set header on every redirect, which would
  otherwise silently drop the cookies before the article loads); the
  Playwright path sets them as `.domain` context cookies. Capped at 8 KB,
  **never logged and never persisted** — there is no cookies column, and
  they are not forwarded to `db.insert_card`.
- **SSRF guard:** before any fetch, the host must resolve to public addresses
  only (`ip.is_global`) — private ranges, loopback, link-local, and cloud
  metadata endpoints are rejected. The httpx path re-checks every redirect
  hop; the browser path checks the initial URL and the final landing URL
  before extracting content. Residual: DNS rebinding between check and fetch,
  and in-page subresource requests, are not intercepted — accepted, since
  only main-frame text reaches a card.
- **Throttling:** `POST /api/cards` is unauthenticated but expensive (function
  time, a billed browser session, an LLM call), so the API keeps a per-IP
  in-memory sliding window (10 ingests / 10 min). Per warm instance only — a
  brake on loops and casual abuse; platform-level rate limiting (e.g. Vercel
  WAF) is the real defense and a follow-up below.
- `vercel.json` sets `maxDuration: 60` for the function: ~20 s browser
  navigation + extraction + the OpenRouter call must fit in one invocation.
  The pipeline tracks a 55 s budget and gives the LLM call the remaining
  time, so a slow fallback fetch fails with a clear error instead of the
  platform killing the function mid-call.

## Consequences

- **Good:** Medium 403s and JS-rendered pages become normal cards; member-only
  content works with the reader's own session; anonymous ingestion is
  unchanged (the fast path is identical); credentials never touch the server
  beyond a single in-flight request.
- **Cost:** fallback ingests take several seconds longer; production needs a
  remote-browser account (`BROWSER_WS_ENDPOINT`) — without it, blocked pages
  fail with a clear "browser rendering is not available" error; the
  `playwright` pip package (~40 MB unzipped, no browser binaries — the build
  never runs `playwright install`) joins the serverless bundle.
- **Risk:** pasted cookies are bearer credentials; they transit HTTPS in the
  request body. The UI says plainly where they live and when they are sent.
  Hosted-browser TLS fingerprints may themselves get flagged by some sites —
  acceptable residual failure, same clean-error behavior as before.

## Open follow-ups

- Verify on the first Vercel preview deploy that the bundle stays under the
  250 MB limit and the build log shows no Chromium download; if the
  `playwright` package proves problematic there, swap the remote path to a
  thin raw-CDP websocket client behind the same function signature.
- Consider surfacing *which* path produced a card (plain vs browser) for
  debugging ingest quality.
- Add platform-level rate limiting (Vercel WAF / firewall rules) for
  `POST /api/cards`; the in-process throttle is per warm instance only.
