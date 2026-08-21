export type CallDirection = 'inbound' | 'outbound' | 'internal' | 'tandem' | 'unknown'
export type CallDisposition = 'answered' | 'abandoned' | 'busy' | 'no_answer' | 'failed' | 'transferred' | 'conferenced' | 'other'

export interface CdrRecord {
  id: number
  ucid: string
  start_time: string
  duration_seconds: number
  ring_duration_seconds: number
  calling_number: string
  dialed_number: string
  direction: CallDirection
  disposition: CallDisposition
  vdn?: string
  agent_extension?: string
  account_code?: string
}

export const sampleCdr: CdrRecord[] = [
  {
    id: 1,
    ucid: "00001001234567890123",
    start_time: "2026-08-20T14:23:17+02:00",
    duration_seconds: 187,
    ring_duration_seconds: 12,
    calling_number: "79031234567",
    dialed_number: "84951234567",
    direction: "inbound",
    disposition: "answered",
    vdn: "3001",
    agent_extension: "1205",
    account_code: "SALES-42",
  },
  {
    id: 2,
    ucid: "00001001234567890124",
    start_time: "2026-08-20T15:10:05+02:00",
    duration_seconds: 45,
    ring_duration_seconds: 8,
    calling_number: "79039876543",
    dialed_number: "84957654321",
    direction: "outbound",
    disposition: "answered",
    vdn: "3002",
    agent_extension: "1208",
  },
  {
    id: 3,
    ucid: "00001001234567890125",
    start_time: "2026-08-20T16:02:33+02:00",
    duration_seconds: 0,
    ring_duration_seconds: 25,
    calling_number: "79031112233",
    dialed_number: "84951112233",
    direction: "inbound",
    disposition: "abandoned",
    vdn: "3001",
  },
]

export function generateMockCdr(count = 100): CdrRecord[] {
  const directions: CallDirection[] = ['inbound', 'outbound', 'internal']
  const dispositions: CallDisposition[] = ['answered', 'abandoned', 'busy', 'no_answer']
  const records: CdrRecord[] = []
  for (let i = 0; i < count; i++) {
    records.push({
      id: i + 1,
      ucid: `0000100${String(i).padStart(12, '0')}`,
      start_time: new Date(Date.now() - Math.random() * 7 * 24 * 3600 * 1000).toISOString(),
      duration_seconds: Math.floor(Math.random() * 600),
      ring_duration_seconds: Math.floor(Math.random() * 30),
      calling_number: `79${Math.floor(Math.random() * 1e9).toString().padStart(9, '0')}`,
      dialed_number: `8495${Math.floor(Math.random() * 1e7).toString().padStart(7, '0')}`,
      direction: directions[Math.floor(Math.random() * directions.length)],
      disposition: dispositions[Math.floor(Math.random() * dispositions.length)],
      vdn: `30${Math.floor(Math.random() * 10)}`,
      agent_extension: `12${Math.floor(Math.random() * 100).toString().padStart(2, '0')}`,
    })
  }
  return records
}
