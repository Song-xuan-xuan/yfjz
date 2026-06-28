import { jsonRequest, requestJson } from './client'
import type { CaseResult, RunCreatePayload, RunDetail, RunSummary } from './types'

export function listRuns(): Promise<RunSummary[]> {
  return requestJson<RunSummary[]>('/runs')
}

export function createRun(payload: RunCreatePayload): Promise<RunSummary> {
  return jsonRequest<RunSummary>('/runs', 'POST', payload)
}

export function getRun(id: number): Promise<RunDetail> {
  return requestJson<RunDetail>(`/runs/${id}`)
}

export function getRunResults(id: number): Promise<CaseResult[]> {
  return requestJson<CaseResult[]>(`/runs/${id}/results`)
}
