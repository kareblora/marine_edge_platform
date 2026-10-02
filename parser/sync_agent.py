import json
import time
import urllib.request
import urllib.error

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
            self.replay_worker.outbox.update_pending_metric()
            connected = self.mqtt_publisher.connect()

            if not connected:

                sync_connection_failure_total.inc()
                print(
                    f"MQTT unavailable. "
                    f"Retrying in "
                    f"{self.retry_interval} seconds."
                )

                self.replay_worker.outbox.update_pending_metric()
                time.sleep(
                    self.retry_interval
                )
                continue
            
            if not self.subscriber_is_ready():
                print("Subscriber is not ready. Waiting before replay.")
                self.mqtt_publisher.disconnect()
                time.sleep(self.retry_interval)
                continue
            
            print("MQTT connection established.")
            print("Subscriber is ready. Starting replay.")

            replayed = self.replay_worker.replay()
            
            self.replay_worker.outbox.update_pending_metric()

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
    
    def subscriber_is_ready(self):
        try:
            response = urllib.request.urlopen(
                "http://localhost:8081/health/ready",
                timeout=2
            )

            return response.status == 200

        except Exception:
            return False
    
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
