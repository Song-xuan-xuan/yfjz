import { jsonRequest, requestJson } from './client'
import type {
  ProviderConfig,
  ProviderConfigCreatePayload,
  ProviderConfigUpdatePayload,
  ProviderTestResponse,
} from './types'

export function listProviderConfigs(): Promise<ProviderConfig[]> {
  return requestJson<ProviderConfig[]>('/provider-configs')
}

export function createProviderConfig(payload: ProviderConfigCreatePayload): Promise<ProviderConfig> {
  return jsonRequest<ProviderConfig>('/provider-configs', 'POST', payload)
}

export function updateProviderConfig(
  id: number,
  payload: ProviderConfigUpdatePayload,
): Promise<ProviderConfig> {
  return jsonRequest<ProviderConfig>(`/provider-configs/${id}`, 'PUT', payload)
}

export function deleteProviderConfig(id: number): Promise<void> {
  return jsonRequest<void>(`/provider-configs/${id}`, 'DELETE')
}

export function testProviderConfig(id: number): Promise<ProviderTestResponse> {
  return jsonRequest<ProviderTestResponse>(`/provider-configs/${id}/test`, 'POST')
}
