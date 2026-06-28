export type RunStatus = 'pending' | 'running' | 'completed' | 'failed'

export type CaseResultStatus = 'pending' | 'running' | 'passed' | 'failed' | 'error'

export type EvaluationType = 'exact_match' | 'contains' | 'regex_match'

export interface HealthResponse {
  status: string
  service: string
}

export interface ProviderConfig {
  id: number
  name: string
  base_url: string
  api_key_masked: string
  default_model: string
  timeout_seconds: number
  max_retries: number
  created_at: string
  updated_at: string
}

export interface ProviderConfigBasePayload {
  name: string
  base_url: string
  default_model: string
  timeout_seconds: number
  max_retries: number
}

export interface ProviderConfigCreatePayload extends ProviderConfigBasePayload {
  api_key: string
}

export interface ProviderConfigUpdatePayload extends ProviderConfigBasePayload {
  api_key?: string
}

export interface ProviderTestResponse {
  ok?: boolean
  status?: string
  message?: string
}

export interface SuiteEvaluation {
  type: EvaluationType
  expected_field: string
  ignore_case?: boolean
  strip?: boolean
}

export interface SuiteCase {
  id: string
  [key: string]: unknown
}

export interface SuiteDefinition {
  name: string
  description?: string
  prompt_template: string
  evaluation: SuiteEvaluation
  cases: SuiteCase[]
}

export interface SuiteCreatePayload {
  suite: SuiteDefinition
}

export interface SuiteListItem {
  id: number
  name: string
  description: string
  case_count: number
  metric_type: EvaluationType
  created_at: string
}

export interface SuiteDetail extends SuiteListItem {
  prompt_template: string
  evaluation: SuiteEvaluation
  cases: SuiteCase[]
}

export interface RunCreatePayload {
  suite_id: number
  provider_config_id: number
  model: string
  temperature: number
  max_tokens: number
  concurrency: 1 | 3 | 5 | 10
  use_cache: boolean
}

export interface RunSummary {
  id: number
  status: RunStatus
  suite_id: number
  provider_config_id: number
  model: string
  total_cases: number
  completed_cases: number
  passed_cases: number
  failed_cases: number
  error_cases: number
  score: number
  created_at: string
}

export interface RunDetail extends RunSummary {
  average_latency_ms?: number
  cache_hit_count?: number
}

export interface CaseResult {
  id: number
  case_id: string
  status: CaseResultStatus
  prompt: string
  expected: string
  output: string | null
  score: number
  reason: string
  latency_ms: number | null
  cache_hit: boolean
  error_message: string | null
}
