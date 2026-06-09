"""FastAPI ASGI app. Vercel serves /api/* from this module's `app`.

Step 1 only wires hosting: a single health endpoint. Later steps add the
cards CRUD (db.py) and the ingest/digest pipeline (digest.py).
"""

from fastapi import FastAPI

app = FastAPI(title="Content Digest API")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
