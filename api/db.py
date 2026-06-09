"""Postgres connection + card queries.

A single `cards` table backs the board. `key_points` and `tags` are JSONB
arrays; everything else is plain columns. See ADR 001 for the Postgres choice.

Connection string comes from DATABASE_URL (Vercel Postgres / Neon locally via a
gitignored .env). We open a short-lived connection per call — fine for the
serverless functions this deploys to, where connection pooling is handled by
the provider's pooled endpoint.
"""

import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

try:
    # Load a local, gitignored .env for dev. On Vercel the real env vars are
    # already set, so this is a no-op there (and optional if not installed).
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url         TEXT        NOT NULL,
    title       TEXT        NOT NULL,
    summary     TEXT        NOT NULL,
    key_points  JSONB       NOT NULL DEFAULT '[]'::jsonb,
    tags        JSONB       NOT NULL DEFAULT '[]'::jsonb,
    category    TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def _dsn() -> str:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set")
    return dsn


def connect() -> psycopg.Connection:
    """Open a connection that returns rows as dicts."""
    return psycopg.connect(_dsn(), row_factory=dict_row)


def init_schema() -> None:
    """Create the cards table if it doesn't exist (idempotent)."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA)
        conn.commit()


def list_cards() -> list[dict]:
    """Return all cards, newest first."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, url, title, summary, key_points, tags, category, created_at
            FROM cards
            ORDER BY created_at DESC, id DESC
            """
        )
        return cur.fetchall()


def insert_card(
    url: str,
    title: str,
    summary: str,
    key_points: list[str],
    tags: list[str],
    category: str,
) -> dict:
    """Insert a card and return the full row (incl. id, created_at)."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cards (url, title, summary, key_points, tags, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, url, title, summary, key_points, tags, category, created_at
            """,
            (
                url,
                title,
                summary,
                Jsonb(key_points),
                Jsonb(tags),
                category,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        return row
