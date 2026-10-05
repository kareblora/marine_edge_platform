from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.cloud_sync_agent import (
    CloudSyncAgent,
    LocalCloudClient,
)
from parser.metrics import start_metrics_server


start_metrics_server(8004)

config = MarineConfig("config/config.json")

publisher_database = (
    config.get_publisher_database()
)

retry_interval = (
    config.get_retry_interval()
)

outbox = TelemetryOutbox(
    publisher_database
)

cloud_client = LocalCloudClient()

cloud_sync_worker = CloudSyncWorker(
    outbox,
    cloud_client
)

cloud_agent = CloudSyncAgent(
    cloud_sync_worker,
    retry_interval
)

try:

    cloud_agent.run()

except KeyboardInterrupt:

    print(
        "Stopping Cloud Sync Agent..."
    )

finally:

    outbox.close()

    print(
        "Cloud Sync Agent stopped."
    )