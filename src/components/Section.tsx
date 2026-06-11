import type { Card as CardData } from '../lib/api'
import Card from './Card'

interface Props {
  category: string
  cards: CardData[]
  categories: string[]
  onCategoryChange: (id: number, category: string) => void
}

export default function Section({
  category,
  cards,
  categories,
  onCategoryChange,
}: Props) {
  return (
    <section className="section">
      <h2 className="section__heading">
        <span className="section__name">{category}</span>
        <span className="section__count">{cards.length}</span>
      </h2>
      <div className="section__cards">
        {cards.map((card) => (
          <Card
            key={card.id}
            card={card}
            categories={categories}
            onCategoryChange={onCategoryChange}
          />
        ))}
      </div>
    </section>
  )
}
