import { useEffect, useState } from 'react'
import { ApiError, createCard, listCards, updateCardCategory } from './lib/api'
import type { Card } from './lib/api'
import UrlInput from './components/UrlInput'
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

  async function handleSubmit(url: string) {
    setSubmitting(true)
    setError(null)
    try {
      const card = await createCard(url)
      setCards((prev) => [card, ...prev])
    } catch (e) {
      setError(
        e instanceof ApiError ? e.message : 'Something went wrong. Try again.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  async function handleCategoryChange(id: number, category: string) {
    const previous = cards
    // Move the card optimistically; revert if the server rejects it.
    setCards((prev) =>
      prev.map((c) => (c.id === id ? { ...c, category } : c)),
    )
    try {
      const updated = await updateCardCategory(id, category)
      setCards((prev) => prev.map((c) => (c.id === id ? updated : c)))
    } catch {
      setCards(previous)
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

      <Board
        cards={cards}
        loading={loading}
        onCategoryChange={handleCategoryChange}
      />
    </main>
  )
}
