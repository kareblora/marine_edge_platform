import json
import logging

from .metrics import cloud_sync_success_total, cloud_sync_failure_total

logger = logging.getLogger("CloudSyncWorker")


class CloudSyncWorker:

    def __init__(self, outbox, cloud_client, batch_size=100):
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        self.outbox = outbox
        self.cloud_client = cloud_client
        self.batch_size = batch_size

    def sync(self, max_messages=None):
        # Use the configured batch size unless explicitly overridden.
        if max_messages is None:
            max_messages = self.batch_size

        if max_messages < 1:
            raise ValueError("max_messages must be at least 1")

        total_synced = 0

        while total_synced < max_messages:
            remaining = max_messages - total_synced
            query_limit = min(100, remaining)

            pending = self.outbox.get_cloud_pending(
                limit=query_limit
            )

            if not pending:
                break

            logger.info(
                "Processing %d pending messages; limit for this run: %d.",
                len(pending),
                max_messages,
            )

            for row in pending:
                message_id = row[0]
                payload = row[1]

                if isinstance(payload, str):
                    payload = json.loads(payload)

                success = self.cloud_client.send(
                    message_id,
                    payload,
                )

                if success:
                    self.outbox.mark_cloud_sent(message_id)
                    cloud_sync_success_total.inc()
                    total_synced += 1
                else:
                    self.outbox.increment_cloud_attempts(message_id)
                    cloud_sync_failure_total.inc()

                    logger.error(
                        "Cloud Synchronization Failed: %s",
                        message_id,
                    )
                    logger.info(
                        "Stopping this run after %d successful deliveries.",
                        total_synced,
                    )
                    return total_synced

        logger.info(
            "Sync complete. Messages synchronized: %d of maximum %d.",
            total_synced,
            max_messages,
        )

        return total_synced

