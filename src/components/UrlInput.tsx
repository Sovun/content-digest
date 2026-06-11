import { useState, type FormEvent } from 'react'

interface Props {
  busy: boolean
  error: string | null
  onSubmit: (url: string) => void
}

// The single obvious action (per PRD): paste a URL, get a card.
export default function UrlInput({ busy, error, onSubmit }: Props) {
  const [url, setUrl] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed || busy) return
    onSubmit(trimmed)
    setUrl('')
  }

  return (
    <form className="url-input" onSubmit={handleSubmit}>
      <div className="url-input__row">
        <input
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste an article URL — get a digest card"
          aria-label="Article URL"
          disabled={busy}
        />
        <button type="submit" disabled={busy}>
          {busy ? 'Distilling…' : 'Digest'}
        </button>
      </div>
      {busy && (
        <p className="url-input__status" role="status">
          Fetching the article, extracting text, writing the digest…
        </p>
      )}
      {error && (
        <p className="url-input__error" role="alert">
          {error}
        </p>
      )}
    </form>
  )
}
