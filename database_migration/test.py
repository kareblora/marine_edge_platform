from parser.outbox import TelemetryOutbox

test_db = "output/outbox_test.db"

outbox = TelemetryOutbox(test_db)

outbox.add(
    "TEST-MESSAGE-001",
    "marine/telemetry/test/dive",
    {
        "message_id": "TEST-MESSAGE-001",
        "timestamp": "2026-10-05T03:30:00",
        "device_id": "TEST-DEVICE",
        "dive_id": "TEST-DIVE"
    }
)

print("Pending:", outbox.get_pending_count())

row = outbox.connection.execute("""
    SELECT
        message_id,
        local_status,
        cloud_status,
        attempts
    FROM outbox
    WHERE message_id = ?
""", ("TEST-MESSAGE-001",)).fetchone()

print(row)

outbox.mark_sent("TEST-MESSAGE-001")

row = outbox.connection.execute("""
    SELECT
        message_id,
        local_status,
        cloud_status,
        attempts
    FROM outbox
    WHERE message_id = ?
""", ("TEST-MESSAGE-001",)).fetchone()

print(row)

outbox.close()