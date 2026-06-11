"""Ingest pipeline: URL → readable text → AI digest.

fetch the URL (httpx) → extract title + body (trafilatura, ADR 002) → one
OpenRouter call for a structured digest (ADR 003) → return the fields to persist.

Any failure along the way raises IngestError with a user-facing message; the
route turns that into a clear error and creates no card (per the PRD).
"""

import json
import os
from urllib.parse import urlparse

import httpx
import trafilatura

# Cap extracted text fed to the model to keep token cost/latency bounded.
MAX_TEXT_CHARS = 12_000

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Model id is config (ADR 003) — swap without code changes.
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"

SYSTEM_PROMPT = (
    "You distill a web article into a compact knowledge card. "
    "Return ONLY a JSON object with exactly these keys: "
    '"summary" (2-4 sentence string), '
    '"key_points" (array of 3-6 short strings), '
    '"tags" (array of 3-7 short lowercase topic strings), '
    '"category" (a single broad topic, Title Case, e.g. "Technology", '
    '"Business", "Science", "Health", "Politics", "Culture"). '
    "No markdown, no commentary — just the JSON object."
)


class IngestError(Exception):
    """Raised when a URL can't be fetched, extracted, or digested."""


def _fetch_html(url: str) -> str:
    # Only http(s) gets fetched or stored — stored URLs become clickable
    # links on the board, so other schemes (javascript:, file:, …) are out.
    if urlparse(url).scheme not in ("http", "https"):
        raise IngestError("Only http(s) URLs are supported.")

    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15.0,
            headers={"User-Agent": "ContentDigest/0.1 (+https://github.com/)"},
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise IngestError(
            f"The page returned HTTP {exc.response.status_code}."
        ) from exc
    except httpx.HTTPError as exc:
        raise IngestError("Could not fetch the URL.") from exc

    if "html" not in resp.headers.get("content-type", "").lower():
        raise IngestError("The URL does not point to an HTML page.")
    return resp.text


def extract(url: str) -> tuple[str, str]:
    """Fetch and extract (title, body). Raises IngestError if unextractable."""
    html = _fetch_html(url)

    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not text or not text.strip():
        raise IngestError(
            "Could not extract readable article text from this page "
            "(it may be paywalled, blocked, or rendered with JavaScript)."
        )

    meta = trafilatura.extract_metadata(html)
    title = (meta.title if meta and meta.title else "").strip() or url
    return title, text.strip()[:MAX_TEXT_CHARS]


def digest(title: str, text: str) -> dict:
    """Call OpenRouter for a structured digest. Raises IngestError on failure."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise IngestError("OPENROUTER_API_KEY is not configured.")

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Title: {title}\n\nArticle:\n{text}",
            },
        ],
    }

    try:
        resp = httpx.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=60.0,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise IngestError("The AI digest request failed.") from exc

    return _parse_digest(content)


def _parse_digest(content: str) -> dict:
    """Validate the model's JSON into the digest shape, or raise IngestError."""
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise IngestError("The AI returned a malformed response.") from exc

    summary = data.get("summary")
    key_points = data.get("key_points")
    tags = data.get("tags")
    category = data.get("category")

    def _str_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(v).strip() for v in value if str(v).strip()]

    summary = summary.strip() if isinstance(summary, str) else ""
    key_points = _str_list(key_points)
    tags = _str_list(tags)
    category = category.strip() if isinstance(category, str) else ""

    if not summary or not key_points or not category:
        raise IngestError("The AI returned an incomplete digest.")

    return {
        "summary": summary,
        "key_points": key_points,
        "tags": tags,
        "category": category,
    }


def ingest(url: str) -> dict:
    """Full pipeline: extract then digest. Returns fields ready to persist."""
    title, text = extract(url)
    result = digest(title, text)
    result["title"] = title
    return result
