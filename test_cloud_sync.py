from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.cloud_client import LocalCloudClient


DATABASE = "output/publisher.db"


outbox = TelemetryOutbox(DATABASE)
cloud_client = LocalCloudClient()

worker = CloudSyncWorker(
    outbox,
    cloud_client
)

print("\n[CLOUD TEST] Starting cloud synchronization...\n")

synced = worker.sync()

print(
    f"\n[CLOUD TEST] Messages synchronized: {synced}"
)

outbox.close()