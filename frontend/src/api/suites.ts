import { jsonRequest, requestJson } from './client'
import type { SuiteCreatePayload, SuiteDetail, SuiteListItem } from './types'

export function listSuites(): Promise<SuiteListItem[]> {
  return requestJson<SuiteListItem[]>('/suites')
}

export function createSuite(payload: SuiteCreatePayload): Promise<SuiteListItem> {
  return jsonRequest<SuiteListItem>('/suites', 'POST', payload)
}

export function getSuite(id: number): Promise<SuiteDetail> {
  return requestJson<SuiteDetail>(`/suites/${id}`)
}

export function deleteSuite(id: number): Promise<void> {
  return jsonRequest<void>(`/suites/${id}`, 'DELETE')
}
