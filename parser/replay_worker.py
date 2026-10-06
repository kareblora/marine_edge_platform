import logging
import json
import time

from .metrics import (
    replay_success_total,
    replay_failure_total,
)

logger = logging.getLogger("ReplayWorker")

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

            logger.info("Processing batch of %d messages.", len(pending))

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

                    self.outbox.increment_local_attempts(
                        message_id
                    )
                    replay_failure_total.inc()

                    logger.error("Replay failed: %s", message_id)

                    # Stop this replay cycle if MQTT
                    # becomes unavailable.
                    return total_replayed

        logger.info(
            "Replay complete. Messages replayed: %d", total_replayed
        )

        return total_replayed
