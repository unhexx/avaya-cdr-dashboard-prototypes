-- Каталог записей для sql-source (MariaDB-совместимый диалект фикстуры).
CREATE TABLE IF NOT EXISTS recording_catalog (
  id               VARCHAR(64) PRIMARY KEY,
  ucid             VARCHAR(32),
  start_time       DATETIME NOT NULL,
  duration         INTEGER,
  caller           VARCHAR(32),
  called           VARCHAR(64),
  path             VARCHAR(512),
  mime_type        VARCHAR(64),
  is_encrypted     TINYINT NOT NULL DEFAULT 0
);

INSERT INTO recording_catalog (id, ucid, start_time, duration, caller, called, path, mime_type, is_encrypted) VALUES
('rec-001', '00001001234567890123', '2026-08-21 14:30:02', 83, '79031234567', '1205', 'placeholder-unencrypted.wav', 'audio/wav', 0),
('rec-002', '00001001234567890125', '2026-08-21 14:32:00', 45, '1206', '84951234001', 'call-00001001234567890125.enc', 'application/octet-stream', 1),
('rec-003', '00001001234567890126', '2026-08-21 14:35:00', 130, '79031234567', '3001', 'call-00001001234567890126.enc', 'application/octet-stream', 1);
