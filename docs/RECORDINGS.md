# RECORDINGS

On-demand playback. Metadata from a **sql-source** (MariaDB or PostgreSQL). Bytes from filesystem path resolved by that metadata. **No decryptor.**

## sql-source

`RECORDINGS_SQL_URL` is a read-only DSN. Adapter maps vendor tables onto `recording_meta`.

Default mapping (override in `extra.mapping` later if needed):

| Canonical | Typical ACR / sidecar column |
|---|---|
| `sql_source_id` | `id` |
| `ucid` | `ucid` / `unique_call_id` / `callid` |
| `start_time` | `start_time` / `created` |
| `duration_seconds` | `duration` |
| `calling_number` | `caller` |
| `dialed_number` | `called` |
| `filename` | `path` / `filename` |
| `encrypted` | `encrypted` / `is_encrypted` / filename suffix `.enc` |

If the url is empty, fixtures in `docs/fixtures/sql/recordings.json` + `docs/fixtures/sql/recordings.sql` load metadata.

`RECORDINGS_MEDIA_ROOT` prefixes relative filenames. Path traversal (`..`) is rejected.

## Encrypted IP Office ≥ R11.1 (law)

Avaya IP Office Voicemail Pro / Media Manager encrypts recordings with platform keys from R11.1 onward (typical default). This project:

- Detects encryption via SQL flag, `.enc` suffix, or fixture `encryption_hint=ipo_r11`.
- Serves **HTTP 409** on `/api/recordings/{id}/audio` with `code=recording_encrypted`, `reason=ipo_encrypted_r11`.
- Still lists the row (duration, numbers, time) so operators know the call was recorded.
- **Does not** ship keys, unwrap AES, or call undocumented VMPro RPCs to obtain plaintext.

Unencrypted placeholder: `docs/fixtures/recordings/placeholder-unencrypted.wav` (tiny PCM).

## Player

SPA uses `<audio>` on a 200 blob URL. On 409, show a Russian explanation: «Запись зашифрована IP Office (R11.1+). Расшифровка недоступна — только метаданные.»

## Join to CDR

See `INTEGRATION_AVAYA.md` (UCID then heuristic). UI “open recording” from CDR detail only if a `recording_meta` row exists.
