BEGIN TRANSACTION;

ALTER TABLE outbox RENAME TO outbox_old;

CREATE TABLE outbox (
    message_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    local_status TEXT NOT NULL DEFAULT 'PENDING',
    cloud_status TEXT NOT NULL DEFAULT 'PENDING',
    local_attempts INTEGER NOT NULL DEFAULT 0,
    cloud_attempts INTEGER NOT NULL DEFAULT 0
);

INSERT INTO outbox (
    message_id,
    topic,
    payload,
    local_status,
    cloud_status,
    local_attempts,
    cloud_attempts
)
SELECT
    message_id,
    topic,
    payload,
    local_status,
    cloud_status,
    attempts,
    0
FROM outbox_old;

DROP TABLE outbox_old;

COMMIT;