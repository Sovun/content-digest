"""FastAPI ASGI app. Vercel serves /api/* from this module's `app`.

Wires hosting (health) and read access to the board (cards). Later steps add
the ingest/digest pipeline (digest.py) behind POST /api/cards.
"""

import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

# Works both locally (uvicorn api.index:app → `api` is a package) and on
# Vercel (which imports the entrypoint with its own dir on sys.path).
try:
    from . import db, digest
except ImportError:  # pragma: no cover
    import db  # type: ignore
    import digest  # type: ignore

app = FastAPI(title="Content Digest API")

# Ensure the schema once per warm instance, lazily on first DB-backed request,
# so a missing DATABASE_URL doesn't crash health checks or cold starts.
_schema_ready = False


def _ensure_schema() -> None:
    global _schema_ready
    if not _schema_ready:
        db.init_schema()
        _schema_ready = True


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cards")
def get_cards() -> list[dict]:
    _ensure_schema()
    return db.list_cards()


class UpdateCategory(BaseModel):
    # Bounded: the category renders as a section heading, so reject
    # arbitrarily long strings at the edge.
    category: str = Field(min_length=1, max_length=100)


@app.patch("/api/cards/{card_id}")
def update_category(card_id: int, body: UpdateCategory) -> dict:
    category = body.category.strip()
    if not category:
        raise HTTPException(status_code=422, detail="A category is required.")

    _ensure_schema()
    row = db.update_card_category(card_id, category)
    if row is None:
        raise HTTPException(status_code=404, detail="Card not found.")
    return row


# Bounded: cookies ride along in the request, so cap them at the edge.
MAX_COOKIES_CHARS = 8_192

# Ingest is expensive (up to 60 s of function time, a billed remote-browser
# session, an LLM call) and the endpoint is unauthenticated — throttle it.
# In-memory, so the limit is per warm instance: a brake on accidental loops
# and casual abuse, not real protection (ADR 004 notes the platform-level
# follow-up).
RATE_LIMIT_MAX_INGESTS = 10
RATE_LIMIT_WINDOW_S = 600
_ingest_log: dict[str, deque[float]] = defaultdict(deque)


def _throttle_ingest(request: Request) -> None:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    now = time.monotonic()
    log = _ingest_log[ip]
    while log and now - log[0] > RATE_LIMIT_WINDOW_S:
        log.popleft()
    if len(log) >= RATE_LIMIT_MAX_INGESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many digest requests — try again in a few minutes.",
        )
    log.append(now)


class CreateCard(BaseModel):
    url: str
    # Optional per-site session cookies for login-gated pages (ADR 004).
    # Used for this one fetch only — never logged, never persisted.
    cookies: dict[str, str] | None = None
    # The domain the user saved those cookies under (e.g. "medium.com" for an
    # article on www.medium.com) — scopes them to that domain and its subdomains.
    cookie_domain: str | None = Field(default=None, max_length=253)


@app.post("/api/cards", status_code=201)
def create_card(body: CreateCard, request: Request) -> dict:
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=422, detail="A URL is required.")

    _throttle_ingest(request)

    cookies = body.cookies or None
    if cookies and sum(len(k) + len(v) for k, v in cookies.items()) > MAX_COOKIES_CHARS:
        raise HTTPException(status_code=422, detail="Cookie data is too large (max 8 KB).")
    cookie_domain = (body.cookie_domain or "").strip().lower().lstrip(".") or None

    try:
        d = digest.ingest(url, cookies=cookies, cookie_domain=cookie_domain)
    except digest.IngestError as exc:
        # Unextractable / failed digest → clear error, no card (per PRD).
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    _ensure_schema()
    return db.insert_card(
        url=url,
        title=d["title"],
        summary=d["summary"],
        key_points=d["key_points"],
        tags=d["tags"],
        category=d["category"],
    )
