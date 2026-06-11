"""FastAPI ASGI app. Vercel serves /api/* from this module's `app`.

Wires hosting (health) and read access to the board (cards). Later steps add
the ingest/digest pipeline (digest.py) behind POST /api/cards.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
    category: str


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


class CreateCard(BaseModel):
    url: str


@app.post("/api/cards", status_code=201)
def create_card(body: CreateCard) -> dict:
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=422, detail="A URL is required.")

    try:
        d = digest.ingest(url)
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
