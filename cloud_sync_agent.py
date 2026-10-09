import logging

from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.cloud_sync_worker import CloudSyncWorker
from parser.cloud_sync_agent import (
    CloudSyncAgent,
    HTTPCloudClient,
)
from parser.logging_config import configure_logging
from parser.metrics import start_metrics_server


configure_logging()

logger = logging.getLogger("CloudSyncAgent")

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

cloud_config = config.get_cloud_config()

cloud_client = HTTPCloudClient(
    endpoint = cloud_config["endpoint"],
    timeout = cloud_config["timeout"],
    region = cloud_config["region"],
)

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

    logger.info("Stopping Cloud Sync Agent...")

finally:

    outbox.close()

    logger.info("Cloud Sync Agent stopped.")
