// Typed fetch wrappers around the FastAPI backend (/api/*).

import type { CookieMatch } from './cookies'

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
  cookieMatch?: CookieMatch,
): Promise<Card> {
  return parseOrThrow<Card>(
    await fetch('/api/cards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(
        cookieMatch
          ? {
              url,
              cookies: cookieMatch.cookies,
              cookie_domain: cookieMatch.domain,
            }
          : { url },
      ),
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
