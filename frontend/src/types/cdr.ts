export type CallDirection = 'inbound' | 'outbound' | 'internal' | 'tandem' | 'unknown';
export type CallDisposition =
  | 'answered'
  | 'abandoned'
  | 'busy'
  | 'no_answer'
  | 'failed'
  | 'transferred'
  | 'conferenced'
  | 'other';

export interface CdrRecord {
  id: number;
  ucid: string;
  call_id?: string;
  start_time: string; // ISO datetime
  answer_time?: string;
  end_time?: string;
  duration_seconds: number;
  ring_duration_seconds: number;
  hold_duration_seconds?: number;
  park_duration_seconds?: number;
  total_duration_seconds?: number;

  calling_number: string;
  dialed_number: string;
  connected_number?: string;
  direction: CallDirection;
  disposition: CallDisposition;

  condition_code?: string;
  access_code_dialed?: string;
  access_code_used?: string;
  trunk_in?: string;
  trunk_out?: string;
  account_code?: string;
  auth_code?: string;
  attendant_console?: string;
  node_number?: string;
  vdn?: string;
  agent_extension?: string;
  agent_id?: string;
  skill_group?: string;

  is_internal: boolean;
  is_transferred: boolean;
  is_conferenced: boolean;
  source_system: string;
  raw_record?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CdrFilters {
  dateFrom?: string;
  dateTo?: string;
  direction?: CallDirection[];
  disposition?: CallDisposition[];
  callingNumber?: string;
  dialedNumber?: string;
  agentExtension?: string;
  vdn?: string;
  accountCode?: string;
  trunk?: string;
  minDuration?: number;
  maxDuration?: number;
  search?: string;
  page?: number;
  pageSize?: number;
  sortBy?: keyof CdrRecord;
  sortOrder?: 'asc' | 'desc';
}

export interface CdrListResponse {
  data: CdrRecord[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface CdrStats {
  totalCalls: number;
  answeredRate: number;
  abandonedRate: number;
  avgDuration: number;
  avgRingTime: number;
  peakHour: number;
  uniqueAgents: number;
  topCallingNumber: string;
  byDirection: Record<string, number>;
  byHour: number[];
  byDayOfWeek: number[];
  byVdn?: Record<string, number>;
  slaPercent?: number;
}
