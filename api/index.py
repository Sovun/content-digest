"""FastAPI ASGI app. Vercel serves /api/* from this module's `app`.

Wires hosting (health) and read access to the board (cards). Later steps add
the ingest/digest pipeline (digest.py) behind POST /api/cards.
"""

from fastapi import FastAPI

# Works both locally (uvicorn api.index:app → `api` is a package) and on
# Vercel (which imports the entrypoint with its own dir on sys.path).
try:
    from . import db
except ImportError:  # pragma: no cover
    import db  # type: ignore

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
