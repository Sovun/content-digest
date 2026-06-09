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

## Open architectural questions (resolve via ADR before building)

- **Text extraction** — browser-only fetch hits CORS limits; likely needs a small
  backend or extraction proxy. Decide before Feature 1.
- **LLM integration** — which model/provider for summary, points, tags, category;
  this is a new runtime dependency and requires an ADR per the working agreement.
