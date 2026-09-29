import json
import time


class ReplayWorker:

    def __init__(self, outbox, mqtt_publisher):
        self.outbox = outbox
        self.mqtt_publisher = mqtt_publisher

    def replay(self):
        pending = self.outbox.get_pending()

        if not pending:
            print("No pending telemetry.")
            return

        print(
            f"Found {len(pending)} pending messages."
        )

        for row in pending:

            message_id = row[0]
            topic = row[1]
            payload = json.loads(row[2])

            print(
                f"Replaying: {message_id}"
            )

            success = self.mqtt_publisher.publish(
                topic,
                payload
            )

            if success:

                self.outbox.mark_sent(
                    message_id
                )

                print(
                    f"Replayed successfully: "
                    f"{message_id}"
                )

            else:

                self.outbox.increment_attempts(
                    message_id
                )

                print(
                    f"Replay failed: "
                    f"{message_id}"
                )