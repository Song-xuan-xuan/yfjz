import type { HealthResponse } from './types'

export const DEFAULT_API_BASE_URL = 'http://localhost:8000/api'

export class ApiError extends Error {
  status: number
  details: unknown

  constructor(message: string, status: number, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

export function resolveApiBaseUrl(configured = import.meta.env.VITE_API_BASE_URL): string {
  const raw = configured?.trim() || DEFAULT_API_BASE_URL
  return raw.replace(/\/+$/, '')
}

function resolveBackendBaseUrl(): string {
  return resolveApiBaseUrl().replace(/\/api$/i, '')
}

function resolveApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${resolveApiBaseUrl()}${normalizedPath}`
}

function resolveBackendUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${resolveBackendBaseUrl()}${normalizedPath}`
}

function resolveErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') {
    return fallback
  }

  const detail = 'detail' in payload ? payload.detail : undefined
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => JSON.stringify(item)).join('; ')
  }
  if ('message' in payload && typeof payload.message === 'string') {
    return payload.message
  }
  return fallback
}

async function parseResponse(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  const text = await response.text()
  if (!text) {
    return null
  }

  try {
    return JSON.parse(text)
  } catch {
    return { message: text }
  }
}

export async function requestJson<T>(
  path: string,
  options: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')

  const response = await fetcher(resolveApiUrl(path), {
    ...options,
    headers,
  })
  const payload = await parseResponse(response as Response)

  if (!response.ok) {
    const message = resolveErrorMessage(payload, `请求失败：HTTP ${response.status}`)
    throw new ApiError(message, response.status, payload)
  }

  return payload as T
}

async function requestBackendJson<T>(
  path: string,
  options: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Accept', 'application/json')

  const response = await fetcher(resolveBackendUrl(path), {
    ...options,
    headers,
  })
  const payload = await parseResponse(response as Response)

  if (!response.ok) {
    const message = resolveErrorMessage(payload, `请求失败：HTTP ${response.status}`)
    throw new ApiError(message, response.status, payload)
  }

  return payload as T
}

export function jsonRequest<T>(path: string, method: string, body?: unknown): Promise<T> {
  const headers = new Headers()
  headers.set('Content-Type', 'application/json')

  return requestJson<T>(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
}

export function getHealth(fetcher: typeof fetch = fetch): Promise<HealthResponse> {
  return requestBackendJson<HealthResponse>('/health', {}, fetcher)
}
