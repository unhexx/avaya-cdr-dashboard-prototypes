/** Типы ответа GET /api/cdr и связанной сводки. */

export type CallDirection =
  | 'inbound'
  | 'outbound'
  | 'internal'
  | 'tandem'
  | 'unknown'

export type CallDisposition =
  | 'answered'
  | 'abandoned'
  | 'busy'
  | 'no_answer'
  | 'failed'
  | 'transferred'
  | 'conferenced'
  | 'other'

export interface CdrRecord {
  id: number
  ucid: string | null
  call_id?: string | null
  start_time: string | null
  duration_seconds: number
  ring_duration_seconds: number
  hold_duration_seconds?: number | null
  park_duration_seconds?: number | null
  calling_number: string | null
  dialed_number: string | null
  connected_number?: string | null
  direction: CallDirection | string
  disposition: CallDisposition | string
  condition_code?: string | null
  trunk_in?: string | null
  trunk_out?: string | null
  account_code?: string | null
  vdn?: string | null
  agent_extension?: string | null
  source_system?: string | null
  is_internal?: boolean
  is_transferred?: boolean
  is_conferenced?: boolean
}

export interface CdrPage {
  items: CdrRecord[]
  page: number
  page_size: number
  total: number
  summary: { count: number; talk_seconds: number }
}

export interface CdrStats {
  total: number
  talk_seconds: number
}

/** Порог SLA в секундах (кольцо до ответа). */
export const SLA_THRESHOLD_SECONDS = 20
