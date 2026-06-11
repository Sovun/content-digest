import type { Card as CardData } from '../lib/api'
import Section from './Section'

interface Props {
  cards: CardData[]
  loading: boolean
  onCategoryChange: (id: number, category: string) => void
}

// Group cards into topic sections, ordered by section size (largest first),
// ties broken alphabetically — the busiest topics lead the page.
function groupByCategory(cards: CardData[]): [string, CardData[]][] {
  const groups = new Map<string, CardData[]>()
  for (const card of cards) {
    const list = groups.get(card.category) ?? []
    list.push(card)
    groups.set(card.category, list)
  }
  return [...groups.entries()].sort(
    ([a, aCards], [b, bCards]) =>
      bCards.length - aCards.length || a.localeCompare(b),
  )
}

export default function Board({ cards, loading, onCategoryChange }: Props) {
  if (loading) {
    return <p className="board__empty">Loading the board…</p>
  }

  if (cards.length === 0) {
    return (
      <div className="board__empty">
        <p className="board__empty-title">Nothing digested yet</p>
        <p>
          Paste an article link above — it comes back as a card with a summary,
          key points, and tags, filed under a topic section.
        </p>
      </div>
    )
  }

  const sections = groupByCategory(cards)
  const categories = sections.map(([name]) => name)

  return (
    <div className="board">
      {sections.map(([category, sectionCards]) => (
        <Section
          key={category}
          category={category}
          cards={sectionCards}
          categories={categories}
          onCategoryChange={onCategoryChange}
        />
      ))}
    </div>
  )
}
