# Recording fixtures

- `placeholder-unencrypted.wav` — tiny PCM WAV for HTTP 200 tests.
- Encrypted IPO ≥ R11.1 samples are **not** stored. See `../sql/recordings.json` (`encrypted: true`, `encryption_hint: ipo_r11`). Audio route must return **409**, never attempt decrypt.

Do not add `.enc` blobs.
