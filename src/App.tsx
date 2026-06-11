import { useEffect, useState } from 'react'
import { ApiError, createCard, listCards, updateCardCategory } from './lib/api'
import type { Card } from './lib/api'
import { getCookiesForUrl } from './lib/cookies'
import UrlInput from './components/UrlInput'
import CookieManager from './components/CookieManager'
import Board from './components/Board'

export default function App() {
  const [cards, setCards] = useState<Card[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listCards()
      .then(setCards)
      .catch(() => setError('Could not load the board. Is the API running?'))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit(url: string): Promise<boolean> {
    setSubmitting(true)
    setError(null)
    try {
      // Attach the user's saved cookies for this site, if any (ADR 004).
      const card = await createCard(url, getCookiesForUrl(url))
      setCards((prev) => [card, ...prev])
      return true
    } catch (e) {
      setError(
        e instanceof ApiError ? e.message : 'Something went wrong. Try again.',
      )
      return false
    } finally {
      setSubmitting(false)
    }
  }

  async function handleCategoryChange(id: number, category: string) {
    const previousCategory = cards.find((c) => c.id === id)?.category
    // Move the card optimistically; revert only this card's category on
    // failure, so concurrent updates to other cards aren't wiped out.
    setCards((prev) =>
      prev.map((c) => (c.id === id ? { ...c, category } : c)),
    )
    try {
      const updated = await updateCardCategory(id, category)
      setCards((prev) => prev.map((c) => (c.id === id ? updated : c)))
    } catch {
      if (previousCategory !== undefined) {
        setCards((prev) =>
          prev.map((c) =>
            c.id === id ? { ...c, category: previousCategory } : c,
          ),
        )
      }
      setError('Could not change the category. Try again.')
    }
  }

  return (
    <main className="app">
      <header className="masthead">
        <h1 className="masthead__title">Content Digest</h1>
        <p className="masthead__tagline">
          Paste a link. Read the digest. The board files it for you.
        </p>
      </header>

      <UrlInput busy={submitting} error={error} onSubmit={handleSubmit} />

      <CookieManager />

      <Board
        cards={cards}
        loading={loading}
        onCategoryChange={handleCategoryChange}
      />
    </main>
  )
}
