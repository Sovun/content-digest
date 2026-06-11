import { useState } from 'react'
import type { Card as CardData } from '../lib/api'

interface Props {
  card: CardData
  categories: string[]
  onCategoryChange: (id: number, category: string) => void
}

const NEW_CATEGORY = '__new__'

function hostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export default function Card({ card, categories, onCategoryChange }: Props) {
  const [naming, setNaming] = useState(false)
  const [newName, setNewName] = useState('')

  function handleSelect(value: string) {
    if (value === NEW_CATEGORY) {
      setNaming(true)
      return
    }
    if (value !== card.category) onCategoryChange(card.id, value)
  }

  function commitNewName() {
    const name = newName.trim()
    setNaming(false)
    setNewName('')
    if (!name) return
    // Reuse an existing section when the name differs only by case,
    // so "ai" doesn't create a second section next to "AI".
    const existing = categories.find(
      (c) => c.toLowerCase() === name.toLowerCase(),
    )
    const category = existing ?? name
    if (category !== card.category) onCategoryChange(card.id, category)
  }

  return (
    <article className="card">
      <header className="card__header">
        <h3 className="card__title">
          <a href={card.url} target="_blank" rel="noreferrer">
            {card.title}
          </a>
        </h3>
        <p className="card__source">
          {hostname(card.url)} ·{' '}
          {new Date(card.created_at).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
          })}
        </p>
      </header>

      <p className="card__summary">{card.summary}</p>

      <ul className="card__points">
        {card.key_points.map((point, i) => (
          <li key={i}>{point}</li>
        ))}
      </ul>

      <footer className="card__footer">
        <ul className="card__tags">
          {card.tags.map((tag, i) => (
            <li key={`${tag}-${i}`}>{tag}</li>
          ))}
        </ul>

        {naming ? (
          <input
            className="card__new-category"
            autoFocus
            value={newName}
            placeholder="New section name"
            aria-label="New category name"
            onChange={(e) => setNewName(e.target.value)}
            onBlur={commitNewName}
            onKeyDown={(e) => {
              if (e.key === 'Enter') commitNewName()
              if (e.key === 'Escape') {
                setNaming(false)
                setNewName('')
              }
            }}
          />
        ) : (
          <select
            className="card__category"
            value={card.category}
            aria-label="Card category"
            onChange={(e) => handleSelect(e.target.value)}
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
            <option value={NEW_CATEGORY}>New section…</option>
          </select>
        )}
      </footer>
    </article>
  )
}
