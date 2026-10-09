import json
import os

from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.cloud_sync_agent import HTTPCloudClient

DATABASE = "/tmp/marine_edge_cloud_worker_test.db"
MESSAGE_ID = "aws-cloud-worker-test-001"

ENDPOINT = (
    "https://cl4xqg6hij.execute-api.us-east-1.amazonaws.com/telemetry"
)

# Start with a clean, isolated test database.
for suffix in ("", "-wal", "-shm"):
    path = DATABASE + suffix
    if os.path.exists(path):
        os.remove(path)

outbox = TelemetryOutbox(DATABASE)

payload = {
    "test": "cloud-sync-worker",
    "depth_m": 8.2,
    "temperature_c": 29.0,
}

# Add one synthetic message to the cloud outbox.
outbox.add(MESSAGE_ID, "marine/test", payload)

# This test concerns cloud delivery only.
# Mark local delivery as SENT so the record resembles an already
# locally delivered message.
outbox.mark_sent(MESSAGE_ID)

print("Before sync:")
print("  Cloud status:", outbox.connection.execute(
    "SELECT cloud_status FROM outbox WHERE message_id = ?",
    (MESSAGE_ID,),
).fetchone()[0])
print("  Pending cloud messages:", outbox.get_cloud_pending_count())

client = HTTPCloudClient(
    endpoint=ENDPOINT,
    timeout=5,
    region="us-east-1",
)

worker = CloudSyncWorker(outbox, client)
synced = worker.sync()

print("\nAfter sync:")
print("  Messages synchronized:", synced)
print("  Cloud status:", outbox.connection.execute(
    "SELECT cloud_status FROM outbox WHERE message_id = ?",
    (MESSAGE_ID,),
).fetchone()[0])
print("  Pending cloud messages:", outbox.get_cloud_pending_count())

outbox.close()
