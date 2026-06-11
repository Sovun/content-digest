"""Ingest pipeline: URL → readable text → AI digest.

fetch the URL (httpx) → extract title + body (trafilatura, ADR 002) → one
OpenRouter call for a structured digest (ADR 003) → return the fields to persist.

Pages the plain fetch can't read (bot-blocked 4xx, JS-rendered) are retried
through a real headless browser (Playwright, ADR 004). User-supplied cookies
ride along for login-gated sites and are never persisted.

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

# Remote browser (Browserless/Browserbase CDP websocket) for deployments that
# can't run Chromium in-process, e.g. Vercel functions (ADR 004). When unset,
# a locally installed Playwright Chromium is launched instead (dev).
BROWSER_WS_ENV = "BROWSER_WS_ENDPOINT"
# Navigation budget; the whole request must also fit OpenRouter's 60s call
# inside the function's maxDuration (vercel.json).
BROWSER_NAV_TIMEOUT_MS = 20_000
# After navigation, give JS rendering / anti-bot interstitials a little time
# to settle into readable text: up to POLLS × POLL_MS extra.
BROWSER_SETTLE_POLLS = 5
BROWSER_SETTLE_POLL_MS = 2_000

# Anti-bot interstitials extract as "text" — never card-ify them.
_CHALLENGE_MARKERS = (
    "security verification",
    "verifying you are not a bot",
    "verify you are human",
    "checking your browser",
    "just a moment",
)

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


class _FetchBlocked(Exception):
    """Plain HTTP fetch was rejected (4xx) — a real browser may still succeed."""


# User-supplied cookie names/values end up in an HTTP header and a browser
# context — strip characters that could inject headers or split cookies.
_COOKIE_BANNED = str.maketrans("", "", "\r\n\0;")


def _sanitize_cookie(value: str) -> str:
    return value.translate(_COOKIE_BANNED)


def _fetch_html(url: str, cookies: dict[str, str] | None = None) -> str:
    # Only http(s) gets fetched or stored — stored URLs become clickable
    # links on the board, so other schemes (javascript:, file:, …) are out.
    if urlparse(url).scheme not in ("http", "https"):
        raise IngestError("Only http(s) URLs are supported.")

    headers = {"User-Agent": "ContentDigest/0.1 (+https://github.com/)"}
    if cookies:
        headers["Cookie"] = "; ".join(
            f"{_sanitize_cookie(k)}={_sanitize_cookie(v)}"
            for k, v in cookies.items()
        )

    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15.0,
            headers=headers,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        # 4xx is typically bot-blocking or a login wall — worth a browser
        # retry. 5xx and network errors are the site's problem; a browser
        # won't help, so they stay terminal.
        if 400 <= status < 500:
            raise _FetchBlocked(f"The page returned HTTP {status}.") from exc
        raise IngestError(f"The page returned HTTP {status}.") from exc
    except httpx.HTTPError as exc:
        raise IngestError("Could not fetch the URL.") from exc

    if "html" not in resp.headers.get("content-type", "").lower():
        raise IngestError("The URL does not point to an HTML page.")
    return resp.text


def _fetch_html_browser(
    url: str, cookies: dict[str, str] | None, reason: str
) -> str:
    """Render the page in headless Chromium and return its HTML (ADR 004).

    `reason` is the user-facing explanation of why the plain fetch wasn't
    enough; it prefixes any error so the user sees the whole story.
    """
    # _fetch_html guards this too, but page.goto would happily open file://
    # and friends — never let a non-web URL reach the browser.
    if urlparse(url).scheme not in ("http", "https"):
        raise IngestError("Only http(s) URLs are supported.")

    try:
        from playwright.sync_api import (
            Error as PlaywrightError,
            TimeoutError as PlaywrightTimeout,
            sync_playwright,
        )
    except ImportError as exc:
        raise IngestError(
            f"{reason} Browser rendering is not available on this deployment."
        ) from exc

    ws_endpoint = os.environ.get(BROWSER_WS_ENV)
    try:
        # The context manager owns cleanup: on exit it disconnects from a
        # remote browser and shuts down a locally launched one.
        with sync_playwright() as pw:
            if ws_endpoint:
                browser = pw.chromium.connect_over_cdp(ws_endpoint)
            else:
                # Dev path. Headless Chromium trips bot detection on the very
                # sites this fallback exists for (Medium serves an unsolvable
                # "security verification" page), while a real headed Chrome
                # passes — so prefer it, parked offscreen. Fall back to
                # headless Chromium when Chrome or a display is missing.
                try:
                    browser = pw.chromium.launch(
                        channel="chrome",
                        headless=False,
                        args=["--window-position=-2400,-2400"],
                    )
                except PlaywrightError:
                    browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            if cookies:
                hostname = urlparse(url).hostname or ""
                context.add_cookies(
                    [
                        {
                            "name": _sanitize_cookie(k),
                            "value": _sanitize_cookie(v),
                            "domain": hostname,
                            "path": "/",
                        }
                        for k, v in cookies.items()
                    ]
                )
            page = context.new_page()
            try:
                resp = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=BROWSER_NAV_TIMEOUT_MS,
                )
            except PlaywrightTimeout:
                resp = None  # use whatever has rendered so far
            # A real browser gets past bot-blocking, so an error status
            # here is genuine (e.g. a 404 page) — don't card-ify it.
            if resp is not None and resp.status >= 400:
                raise IngestError(f"The page returned HTTP {resp.status}.")
            # Let client-side rendering / bot checks settle into
            # readable article text before giving up on the page.
            html = page.content()
            for _ in range(BROWSER_SETTLE_POLLS):
                text = _extract_text(html)
                if text and not _looks_like_challenge(text):
                    break
                page.wait_for_timeout(BROWSER_SETTLE_POLL_MS)
                html = page.content()
            text = _extract_text(html)
            if text and _looks_like_challenge(text):
                raise IngestError(
                    f"{reason} The site presented a bot-verification "
                    "check the browser could not pass."
                )
            return html
    except PlaywrightError:
        # `from None`: Playwright errors can quote cookie values (e.g. a
        # rejected add_cookies call) — keep credentials out of the chain.
        raise IngestError(f"{reason} Browser rendering also failed.") from None


def _looks_like_challenge(text: str) -> bool:
    """True if extracted "text" is an anti-bot interstitial, not an article."""
    lowered = text.lower()
    return any(marker in lowered for marker in _CHALLENGE_MARKERS)


def _extract_text(html: str) -> str | None:
    """Readable body text from HTML, or None if there is none."""
    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not text or not text.strip():
        return None
    return text.strip()[:MAX_TEXT_CHARS]


def extract(url: str, cookies: dict[str, str] | None = None) -> tuple[str, str]:
    """Fetch and extract (title, body). Raises IngestError if unextractable.

    Tries a plain httpx fetch first; if the site blocks it (4xx) or the page
    has no readable text (JS-rendered), retries once with a headless browser.
    """
    html: str | None = None
    text: str | None = None
    reason = None
    try:
        html = _fetch_html(url, cookies)
        text = _extract_text(html)
        if text is None:
            reason = (
                "Could not extract readable article text from this page "
                "(it may be rendered with JavaScript)."
            )
    except _FetchBlocked as exc:
        reason = str(exc)

    if text is None:
        html = _fetch_html_browser(url, cookies, reason or "")
        text = _extract_text(html)
        if text is None:
            raise IngestError(
                "Could not extract readable article text from this page, "
                "even with browser rendering (it may be paywalled or "
                "login-gated)."
            )

    meta = trafilatura.extract_metadata(html)
    title = (meta.title if meta and meta.title else "").strip() or url
    return title, text


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


def ingest(url: str, cookies: dict[str, str] | None = None) -> dict:
    """Full pipeline: extract then digest. Returns fields ready to persist.

    `cookies` are user-supplied per-site session cookies (ADR 004): used only
    for this fetch, never logged, never persisted.
    """
    title, text = extract(url, cookies)
    result = digest(title, text)
    result["title"] = title
    return result
