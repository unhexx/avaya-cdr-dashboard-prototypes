# CM CDR fixtures

| File | Format |
|---|---|
| `unformatted.txt` | space-padded unformatted |
| `expanded.txt` | expanded with date + UCID |
| `customized.txt` | pipe-delimited customized |
| `sat/*.txt` | read-only SAT command output |

Condition code `9` in these samples maps to inbound answered unless the parser table says otherwise; keep `raw_record` regardless.
