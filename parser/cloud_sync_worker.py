from .metrics import (
    cloud_sync_success_total,
    cloud_sync_failure_total,
)


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

            print(
                f"[CLOUD SYNC] Processing "
                f"{len(pending)} messages."
            )

            for row in pending:

                message_id = row[0]
                payload = row[1]

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

                    print(
                        f"[CLOUD SYNC] Failed: "
                        f"{message_id}"
                    )

                    return total_synced

        print(
            f"[CLOUD SYNC] Sync complete. "
            f"Messages synchronized: {total_synced}"
        )

        return total_synced