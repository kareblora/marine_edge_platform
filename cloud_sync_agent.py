import logging
import os

from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.cloud_sync_agent import (
    CloudSyncAgent,
    HTTPCloudClient,
)
from parser.logging_config import configure_logging
from parser.metrics import start_metrics_server

class SimulatedCloudClient:
    def send(self, message_id, payload):
        logger.info(
            "[SIMULATION] Would deliver message %s",
            message_id,
        )
        return True

configure_logging()

logger = logging.getLogger("CloudSyncAgent")

start_metrics_server(8004)

config_path = os.environ.get(
    "MARINE_CONFIG",
    "config/config.json",
)

config = MarineConfig(config_path)


publisher_database = (
    config.get_publisher_database()
)

outbox = TelemetryOutbox(
    publisher_database
)

cloud_config = config.get_cloud_config()

retry_interval = cloud_config["retry_interval_seconds"]
batch_size = cloud_config["batch_size"]

if os.environ.get("MARINE_CLOUD_SIMULATION") == "1":
    logger.warning("SIMULATION MODE ENABLED: no AWS requests will be sent")
    cloud_client = SimulatedCloudClient()
else:
    cloud_client = HTTPCloudClient(
        endpoint=cloud_config["endpoint"],
        timeout=cloud_config["timeout"],
        region=cloud_config["region"],
    )

cloud_sync_worker = CloudSyncWorker(
    outbox,
    cloud_client,
    batch_size=batch_size,
)

cloud_agent = CloudSyncAgent(
    cloud_sync_worker,
    retry_interval
)

try:

    cloud_agent.run()

except KeyboardInterrupt:

    logger.info("Stopping Cloud Sync Agent...")

finally:

    outbox.close()

    logger.info("Cloud Sync Agent stopped.")
