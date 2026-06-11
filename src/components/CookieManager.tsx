import { useState, type FormEvent } from 'react'
import {
  listCookieDomains,
  normalizeDomain,
  parseCookieInput,
  removeCookiesForDomain,
  saveCookiesForDomain,
} from '../lib/cookies'

// Collapsed-by-default panel for per-site session cookies (ADR 004), so a
// member-only article can be digested with the reader's own session.
export default function CookieManager() {
  const [domains, setDomains] = useState<string[]>(listCookieDomains)
  const [domain, setDomain] = useState('')
  const [raw, setRaw] = useState('')
  const [error, setError] = useState<string | null>(null)

  function handleSave(e: FormEvent) {
    e.preventDefault()
    const d = normalizeDomain(domain)
    if (!d) return
    const cookies = parseCookieInput(raw)
    if (Object.keys(cookies).length === 0) {
      setError('Could not parse any cookies from the pasted text.')
      return
    }
    saveCookiesForDomain(d, cookies)
    setDomains(listCookieDomains())
    setDomain('')
    setRaw('')
    setError(null)
  }

  function handleRemove(d: string) {
    removeCookiesForDomain(d)
    setDomains(listCookieDomains())
  }

  return (
    <details className="cookie-mgr">
      <summary className="cookie-mgr__toggle">
        Site cookies{' '}
        <span className="cookie-mgr__hint">for login-gated articles</span>
      </summary>
      <div className="cookie-mgr__body">
        <p className="cookie-mgr__note">
          Paste your session cookies for a site (a Cookie header value or
          cookies.txt lines). They stay in this browser and are sent only when
          you digest a matching URL — the server never stores them.
        </p>
        <form className="cookie-mgr__form" onSubmit={handleSave}>
          <input
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="Site domain, e.g. medium.com"
            aria-label="Site domain"
            required
          />
          <textarea
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            placeholder="name=value; name2=value2 — or cookies.txt lines"
            aria-label="Cookie data"
            rows={3}
            required
          />
          <button type="submit">Save cookies</button>
        </form>
        {error && (
          <p className="cookie-mgr__error" role="alert">
            {error}
          </p>
        )}
        {domains.length > 0 && (
          <ul className="cookie-mgr__list">
            {domains.map((d) => (
              <li key={d}>
                {d}
                <button
                  type="button"
                  onClick={() => handleRemove(d)}
                  aria-label={`Remove cookies for ${d}`}
                >
                  remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </details>
  )
}
