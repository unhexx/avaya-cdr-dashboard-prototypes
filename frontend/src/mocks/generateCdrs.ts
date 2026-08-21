import type { CdrRecord, CallDirection, CallDisposition } from '../types/cdr';

const russianPrefixes = ['7903', '7905', '7916', '7926', '7495', '7499', '7812', '7383'];
const extensions = Array.from({ length: 50 }, (_, i) => String(1000 + i));
const vdns = ['3001', '3002', '3003', '3100', '3200', '4001', 'sales', 'support'];
const trunks = ['T01', 'T02', 'T03', 'T07', 'T12', 'PRI1', 'SIP1'];
const accountCodes = ['SALES-01', 'SUPPORT-12', 'PROJ-42', 'HR-07', 'IT-99'];

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generatePhone(): string {
  const prefix = randomItem(russianPrefixes);
  return prefix + String(randomInt(1000000, 9999999)).padStart(7, '0');
}

function generateUcid(): string {
  return '0000' + String(Date.now()).slice(-10) + String(randomInt(100000, 999999));
}

/**
 * Generate realistic Avaya-style CDR records with business-hour bias,
 * peak periods, realistic answer rates and duration distribution.
 */
export function generateCdrRecords(count: number = 5000, daysBack: number = 30): CdrRecord[] {
  const records: CdrRecord[] = [];
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const dayOffset = randomInt(0, daysBack);
    const date = new Date(now);
    date.setDate(date.getDate() - dayOffset);

    // Prefer weekdays
    if (date.getDay() === 0 || date.getDay() === 6) {
      if (Math.random() > 0.3) {
        date.setDate(date.getDate() - (date.getDay() === 0 ? 2 : 1));
      }
    }

    // Hour bias: peak 10-12 and 14-16
    let hour = randomInt(7, 21);
    if (Math.random() < 0.6) hour = randomInt(9, 17);
    if (Math.random() < 0.3) hour = randomItem([10, 11, 14, 15]);
    date.setHours(hour, randomInt(0, 59), randomInt(0, 59), 0);

    const finalDirection: CallDirection =
      Math.random() < 0.45 ? 'inbound' :
      Math.random() < 0.7 ? 'outbound' :
      Math.random() < 0.9 ? 'internal' : 'tandem';

    // Duration distribution: many short, some long
    let duration = 0;
    const r = Math.random();
    if (r < 0.15) duration = randomInt(0, 15);
    else if (r < 0.55) duration = randomInt(20, 120);
    else if (r < 0.85) duration = randomInt(120, 300);
    else if (r < 0.95) duration = randomInt(300, 900);
    else duration = randomInt(900, 3600);

    const ring = randomInt(3, 45);
    const isAnswered = Math.random() > 0.18; // ~82% answer rate

    let disposition: CallDisposition;
    if (!isAnswered) {
      disposition = randomItem(['abandoned', 'no_answer', 'busy'] as CallDisposition[]);
      duration = 0;
    } else if (Math.random() < 0.08) {
      disposition = 'transferred';
    } else if (Math.random() < 0.03) {
      disposition = 'conferenced';
    } else {
      disposition = 'answered';
    }

    const calling = finalDirection === 'inbound' ? generatePhone() : randomItem(extensions);
    const dialed =
      finalDirection === 'outbound' ? generatePhone() :
      finalDirection === 'internal' ? randomItem(extensions) :
      randomItem(extensions);

    const agent =
      finalDirection !== 'outbound' && Math.random() > 0.3
        ? randomItem(extensions)
        : undefined;

    const record: CdrRecord = {
      id: i + 1,
      ucid: generateUcid(),
      start_time: date.toISOString(),
      duration_seconds: duration,
      ring_duration_seconds: isAnswered ? ring : randomInt(10, 60),
      calling_number: calling,
      dialed_number: dialed,
      direction: finalDirection,
      disposition,
      vdn: Math.random() > 0.4 ? randomItem(vdns) : undefined,
      agent_extension: agent,
      trunk_in: finalDirection === 'inbound' ? randomItem(trunks) : undefined,
      trunk_out: finalDirection === 'outbound' ? randomItem(trunks) : undefined,
      account_code: Math.random() > 0.6 ? randomItem(accountCodes) : undefined,
      is_internal: finalDirection === 'internal',
      is_transferred: disposition === 'transferred',
      is_conferenced: disposition === 'conferenced',
      source_system: 'mock',
    };

    if (isAnswered && duration > 0) {
      const end = new Date(date.getTime() + (ring + duration) * 1000);
      record.answer_time = new Date(date.getTime() + ring * 1000).toISOString();
      record.end_time = end.toISOString();
    }

    records.push(record);
  }

  records.sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  return records;
}

/** Pre-generated dataset for all prototypes */
export const MOCK_CDR_DATA: CdrRecord[] = generateCdrRecords(5000);
