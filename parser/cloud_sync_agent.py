import time

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

        print("[CLOUD SYNC] Cloud Sync Agent started.")
        print(
            f"[CLOUD SYNC] Retry interval: "
            f"{self.retry_interval} seconds"
        )

        while True:

            synced = self.cloud_sync_worker.sync()

            print(
                f"[CLOUD SYNC] Sync cycle completed. "
                f"Messages synchronized: {synced}"
            )

            time.sleep(
                self.retry_interval
            )