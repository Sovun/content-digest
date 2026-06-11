// Per-site session cookies for login-gated articles (ADR 004).
// Stored only in this browser's localStorage; sent with a digest request
// only when the article's host matches. The server uses them for that one
// fetch and never persists them.

const STORAGE_PREFIX = 'cd:cookies:'

// If the user pastes a Set-Cookie line instead of a Cookie header, its
// attributes would otherwise become phantom cookies.
const SET_COOKIE_ATTRS = new Set([
  'path',
  'domain',
  'expires',
  'max-age',
  'httponly',
  'secure',
  'samesite',
  'partitioned',
  'priority',
])

/** Parse a pasted cookie blob into name → value pairs.
 *
 * Accepts a Cookie header value ("a=1; b=2", optionally prefixed with
 * "Cookie:") or Netscape cookies.txt lines (7 tab-separated fields). */
export function parseCookieInput(raw: string): Record<string, string> {
  const pairs: Record<string, string> = {}
  const body = raw.trim().replace(/^cookie:\s*/i, '')
  for (const line of body.split('\n')) {
    const l = line.trim()
    if (!l || l.startsWith('#')) continue
    const fields = l.split('\t')
    if (fields.length >= 7) {
      // cookies.txt: domain flag path secure expiry NAME VALUE
      const name = fields[5].trim()
      if (name) pairs[name] = fields[6].trim()
      continue
    }
    // Cookie header value: name=value pairs separated by semicolons.
    for (const part of l.split(';')) {
      const idx = part.indexOf('=')
      if (idx <= 0) continue
      const name = part.slice(0, idx).trim()
      if (SET_COOKIE_ATTRS.has(name.toLowerCase())) continue
      pairs[name] = part.slice(idx + 1).trim()
    }
  }
  return pairs
}

/** "https://www.medium.com/path" or "Medium.com/" → "www.medium.com" */
export function normalizeDomain(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .split('/')[0]
}

export function saveCookiesForDomain(
  domain: string,
  cookies: Record<string, string>,
): void {
  localStorage.setItem(STORAGE_PREFIX + domain, JSON.stringify(cookies))
}

export function removeCookiesForDomain(domain: string): void {
  localStorage.removeItem(STORAGE_PREFIX + domain)
}

export function listCookieDomains(): string[] {
  return Object.keys(localStorage)
    .filter((k) => k.startsWith(STORAGE_PREFIX))
    .map((k) => k.slice(STORAGE_PREFIX.length))
    .sort()
}

/** Cookies saved for the URL's host (or a parent domain), if any. */
export function getCookiesForUrl(
  url: string,
): Record<string, string> | undefined {
  try {
    const host = new URL(url).hostname.toLowerCase()
    // Most specific match wins: prefer "sub.medium.com" over "medium.com".
    const matches = listCookieDomains()
      .filter((d) => host === d || host.endsWith('.' + d))
      .sort((a, b) => b.length - a.length)
    for (const domain of matches) {
      const raw = localStorage.getItem(STORAGE_PREFIX + domain)
      if (raw) return JSON.parse(raw) as Record<string, string>
    }
  } catch {
    // Malformed URL or corrupted storage — behave as if no cookies exist.
  }
  return undefined
}
