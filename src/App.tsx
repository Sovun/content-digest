import { useEffect, useState } from 'react'

// Step 1 placeholder: confirm the frontend can reach the FastAPI /api/health
// endpoint through the dev proxy (and Vercel routing in production).
export default function App() {
  const [health, setHealth] = useState<string>('checking…')

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => setHealth(d.status ?? 'unknown'))
      .catch(() => setHealth('unreachable'))
  }, [])

  return (
    <main>
      <h1>Content Digest</h1>
      <p>
        API health: <strong>{health}</strong>
      </p>
    </main>
  )
}
