# Content Digest — PRD

## Problem & who it's for

People save far more articles than they ever read. Read-later lists become graveyards:
flat, undifferentiated, and growing. The cost of revisiting a saved link (open it, skim
it, decide if it still matters) is high enough that most never get reopened.

**Content Digest** turns a pasted link into a self-organizing knowledge card. Paste a
URL → the app extracts the article text → AI writes a short summary, pulls key points
and tags, and **suggests a category** → the result lands as a **card on a topic-sectioned
board**. The reader skims digests instead of articles, and the board organizes itself.

**For:** a reader/knowledge worker who collects more articles than they can keep up with
and wants them distilled and auto-organized rather than piled in a list.

## Core user scenarios (feature list)

1. **Paste a link** — user pastes an article URL; the app fetches the page and extracts
   the readable title and body, stripping nav, ads, and boilerplate.
2. **Get an AI digest** — for the extracted text, the app generates a short summary, a
   list of key points, and a set of tags.
3. **See a suggested category** — the app proposes a single category for the article; the
   user can accept it or override it.
4. **Read it as a card on a board** — each processed article becomes a card placed on a
   board whose sections are organized by topic/category; overriding the category moves the
   card to the matching section.
5. **Handle failures gracefully** — if a URL can't be fetched or the article can't be
   extracted, the user sees a clear error and the card is not created.

## In scope (MVP)

- URL ingestion + readable-text extraction (title + body).
- AI-generated summary, key points, and tags.
- AI category suggestion with manual override.
- Topic-sectioned board of cards; cards move when category changes.
- Clear error states for fetch/extraction failures.

## Out of scope (MVP)

- Accounts, auth, multi-user sync.
- Full-text search across saved articles.
- Editing the source article text or the generated digest.
- Mobile-native apps (web only).
- Bulk import, browser extension, scheduled re-fetching.

## MVP success criteria

- Pasting a valid article URL produces a card with a **non-empty** summary, key points,
  tags, and a suggested category — with **no manual text entry**.
- Cards appear under the board section matching their category; overriding the category
  moves the card to the correct section.
- An invalid or unextractable URL yields a clear error and creates **no** card.
- The end-to-end paste → card flow completes in a single, obvious user action.
