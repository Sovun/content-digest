// Typed fetch wrappers around the FastAPI backend (/api/*).

export interface Card {
  id: number
  url: string
  title: string
  summary: string
  key_points: string[]
  tags: string[]
  category: string
  created_at: string
}

export class ApiError extends Error {}

async function parseOrThrow<T>(resp: Response): Promise<T> {
  const body = await resp.json().catch(() => null)
  if (!resp.ok) {
    const detail =
      body && typeof body.detail === 'string'
        ? body.detail
        : `Request failed (HTTP ${resp.status}).`
    throw new ApiError(detail)
  }
  return body as T
}

export async function listCards(): Promise<Card[]> {
  return parseOrThrow<Card[]>(await fetch('/api/cards'))
}

export async function createCard(
  url: string,
  cookies?: Record<string, string>,
): Promise<Card> {
  return parseOrThrow<Card>(
    await fetch('/api/cards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cookies ? { url, cookies } : { url }),
    }),
  )
}

export async function updateCardCategory(
  id: number,
  category: string,
): Promise<Card> {
  return parseOrThrow<Card>(
    await fetch(`/api/cards/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category }),
    }),
  )
}
