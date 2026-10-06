import time
import logging

logger = logging.getLogger("CloudSyncAgent")
client_logger = logging.getLogger("LocalCloudClient")


class LocalCloudClient:
    
    def send(self, message_id, payload):
        client_logger.info("Sending message: %s", message_id)

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
