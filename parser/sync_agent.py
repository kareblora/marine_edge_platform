import json
import time

from .metrics import (
    sync_attempt_total,
    sync_connection_failure_total,
)

class EdgeSyncAgent:

    def __init__(
        self,
        replay_worker,
        mqtt_publisher,
        retry_interval=10
    ):
        self.replay_worker = replay_worker
        self.mqtt_publisher = mqtt_publisher
        self.retry_interval = retry_interval

    def run(self):

        print("Edge Sync Agent started.")

        while True:

            sync_attempt_total.inc()
            connected = self.mqtt_publisher.connect()

            if not connected:

                sync_connection_failure_total.inc()
                print(
                    f"MQTT unavailable. "
                    f"Retrying in "
                    f"{self.retry_interval} seconds."
                )

                time.sleep(
                    self.retry_interval
                )

                continue

            print("MQTT connection established.")

            #replayed = self.replay_pending()
            replayed = self.replay_worker.replay()

            self.mqtt_publisher.disconnect()

            if replayed == 0:

                print(
                    "No pending telemetry. "
                    f"Next check in "
                    f"{self.retry_interval} seconds."
                )

            time.sleep(
                self.retry_interval
            )

    def replay_pending(self):

        total_replayed = 0

        while True:

            pending = self.outbox.get_pending(
                limit=100
            )

            if not pending:
                break

            print(
                f"Replaying batch: "
                f"{len(pending)} messages"
            )

            for row in pending:

                message_id = row[0]
                topic = row[1]
                payload = json.loads(row[2])

                success = (
                    self.mqtt_publisher.publish(
                        topic,
                        payload
                    )
                )

                if success:

                    self.outbox.mark_sent(
                        message_id
                    )

                    total_replayed += 1

                else:

                    self.outbox.increment_attempts(
                        message_id
                    )

                    print(
                        f"Replay failed: "
                        f"{message_id}"
                    )

                    return total_replayed

        if total_replayed > 0:

            print(
                f"Replay complete: "
                f"{total_replayed} messages"
            )

        return total_replayed
