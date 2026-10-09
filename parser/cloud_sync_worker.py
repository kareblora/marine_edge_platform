import logging
import json

from .metrics import (
    cloud_sync_success_total,
    cloud_sync_failure_total,
)

logger = logging.getLogger("CloudSyncWorker")

class CloudSyncWorker:

    def __init__(
        self,
        outbox,
        cloud_client,
    ):
        self.outbox = outbox
        self.cloud_client = cloud_client

    def sync(self):
        total_synced = 0

        while True:

            pending = self.outbox.get_cloud_pending(
                limit=100
            )

            if not pending:
                break

            logger.info( "Processing %d pending messages.", len(pending))

            for row in pending:

                message_id = row[0]
                payload = row[1]

                if isinstance(payload, str):
                    payload = json.loads(payload)

                success = self.cloud_client.send(
                    message_id,
                    payload
                )

                if success:

                    self.outbox.mark_cloud_sent(
                        message_id
                    )

                    cloud_sync_success_total.inc()

                    total_synced += 1

                else:

                    self.outbox.increment_cloud_attempts(
                        message_id
                    )

                    cloud_sync_failure_total.inc()

                    logger.error("Cloud Synchronization Failed: %s", message_id)

                    return total_synced

        logger.info(
            "Sync complete. Messages synchronized: %d",
            total_synced
        )

        return total_synced
