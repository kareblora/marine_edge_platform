import time
import logging

from .logging_config import configure_logging

configure_logging()
logger = logging.getLogger("CloudSyncAgent")


class LocalCloudClient:
    
    def send(self, message_id, payload):
        print(
            f"[CLOUD CLIENT] Sending message: "
            f"{message_id}"
        )

        return True

class CloudSyncAgent:

    def __init__(
        self,
        cloud_sync_worker,
        retry_interval=10,
    ):
        self.cloud_sync_worker = cloud_sync_worker
        self.retry_interval = retry_interval

    def run(self):

        logger.info("Cloud Sync Agent started.")
        logger.info("Retry interval: %s seconds", self.retry_interval)

        while True:

            self.cloud_sync_worker.outbox.update_cloud_pending_metric()
            
            synced = self.cloud_sync_worker.sync()
            
            self.cloud_sync_worker.outbox.update_cloud_pending_metric()

            logger.info("Sync cycle completed. Messages synchronized: %s", synced)

            time.sleep(
                self.retry_interval
            )