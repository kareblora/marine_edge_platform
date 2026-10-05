sqlite3 output/publisher.db

BEGIN TRANSACTION;

ALTER TABLE outbox RENAME TO outbox_old;

CREATE TABLE outbox (
    message_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,

    local_status TEXT NOT NULL DEFAULT 'PENDING',
    cloud_status TEXT NOT NULL DEFAULT 'PENDING',

    attempts INTEGER NOT NULL DEFAULT 0
);

INSERT INTO outbox (
    message_id,
    topic,
    payload,
    local_status,
    cloud_status,
    attempts
)
SELECT
    message_id,
    topic,
    payload,
    status,
    'PENDING',
    attempts
FROM outbox_old;

DROP TABLE outbox_old;

COMMIT;

#-----

SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN local_status = 'PENDING' THEN 1 ELSE 0 END) AS local_pending,
    SUM(CASE WHEN local_status = 'SENT' THEN 1 ELSE 0 END) AS local_sent,
    SUM(CASE WHEN cloud_status = 'PENDING' THEN 1 ELSE 0 END) AS cloud_pending,
    SUM(CASE WHEN cloud_status = 'SENT' THEN 1 ELSE 0 END) AS cloud_sent
FROM outbox;