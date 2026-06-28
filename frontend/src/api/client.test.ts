import { describe, expect, test, vi } from 'vitest'
import { ApiError, getHealth, requestJson, resolveApiBaseUrl } from './client'

describe('resolveApiBaseUrl', () => {
  test('uses the default backend API URL when env is empty', () => {
    expect(resolveApiBaseUrl()).toBe('http://localhost:8000/api')
  })

  test('removes trailing slashes from configured API URL', () => {
    expect(resolveApiBaseUrl('http://localhost:9000/api///')).toBe('http://localhost:9000/api')
  })
})

describe('requestJson', () => {
  test('parses JSON responses from the configured API base URL', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ status: 'ok' }),
      text: async () => '',
    })

    const result = await requestJson<{ status: string }>('/suites', {}, fetchMock)

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/suites',
      expect.objectContaining({ headers: expect.any(Headers) }),
    )
    const [, init] = fetchMock.mock.calls[0]
    expect((init?.headers as Headers).get('Accept')).toBe('application/json')
    expect(result).toEqual({ status: 'ok' })
  })

  test('throws ApiError with backend message for failed responses', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ detail: 'JSON 格式错误' }),
      text: async () => '',
    })

    await expect(requestJson('/suites', {}, fetchMock)).rejects.toMatchObject({
      message: 'JSON 格式错误',
      status: 422,
    })
    await expect(requestJson('/suites', {}, fetchMock)).rejects.toBeInstanceOf(ApiError)
  })
})

describe('getHealth', () => {
  test('checks the backend root health endpoint outside the /api prefix', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ status: 'ok', service: 'yfjz-backend' }),
      text: async () => '',
    })

    const result = await getHealth(fetchMock)

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/health',
      expect.objectContaining({ headers: expect.any(Headers) }),
    )
    expect(result).toEqual({ status: 'ok', service: 'yfjz-backend' })
  })
})
