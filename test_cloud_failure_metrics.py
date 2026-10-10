import os
import time
import threading
from http.server import HTTPServer

from prometheus_client import (
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_client.core import REGISTRY
from prometheus_client import start_http_server

from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.metrics import (
    cloud_sync_success_total,
    cloud_sync_failure_total,
    cloud_pending_messages,
)

DB = "/tmp/marine_edge_failure_metrics.db"

# Reset only this isolated test database.
for suffix in ("", "-wal", "-shm"):
    path = DB + suffix
    if os.path.exists(path):
        os.remove(path)

outbox = TelemetryOutbox(DB)

outbox.add(
    "live-failure-metric-test-001",
    "marine/test",
    {"test": "failure-metrics"},
)

class FailingCloudClient:
    def send(self, message_id, payload):
        print(f"Simulated delivery failure: {message_id}")
        return False

# Start a separate metrics endpoint on port 8005.
start_http_server(8005)

outbox.update_cloud_pending_metric()

worker = CloudSyncWorker(
    outbox,
    FailingCloudClient(),
    batch_size=10,
)

print("Pending before sync:", outbox.get_cloud_pending_count())

synced = worker.sync()

outbox.update_cloud_pending_metric()

print("Messages synchronized:", synced)
print("Pending after sync:", outbox.get_cloud_pending_count())

print("\nMetrics endpoint: http://localhost:8005/metrics")
print("Keep this script running while you query the endpoint.")
print("Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping failure-metrics test.")
finally:
    outbox.close()
