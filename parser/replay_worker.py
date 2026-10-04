import json
import time

from .metrics import (
    replay_success_total,
    replay_failure_total,
)

class ReplayWorker:

    def __init__(self, outbox, mqtt_publisher):
        self.outbox = outbox
        self.mqtt_publisher = mqtt_publisher

    def replay(self):
        total_replayed = 0

        while True:

            pending = self.outbox.get_pending(limit=100)

            if not pending:
                break

            print(
                f"Processing batch of {len(pending)} messages."
            )

            for row in pending:

                message_id = row[0]
                topic = row[1]
                payload = json.loads(row[2])

                success = self.mqtt_publisher.publish(
                    topic,
                    payload
                )

                if success:

                    self.outbox.mark_sent(
                        message_id
                    )
                    replay_success_total.inc()

                    total_replayed += 1

                else:

                    self.outbox.increment_attempts(
                        message_id
                    )
                    replay_failure_total.inc()

                    print(
                        f"Replay failed: {message_id}"
                    )

                    # Stop this replay cycle if MQTT
                    # becomes unavailable.
                    return total_replayed

        print(
            f"Replay complete. "
            f"Messages replayed: {total_replayed}"
        )

        return total_replayed
