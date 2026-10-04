import time
import urllib.request

from .metrics import (
    sync_attempt_total,
    sync_connection_failure_total,
)

class EdgeSyncAgent:

    def __init__(
        self,
        replay_worker,
        mqtt_publisher,
        retry_interval=10,
        health_host="localhost",
        health_port=8081
    ):
        self.replay_worker = replay_worker
        self.mqtt_publisher = mqtt_publisher
        self.retry_interval = retry_interval
        self.health_host = health_host
        self.health_port = health_port
        
        self.health_url = (
            f"http://{self.health_host}:{self.health_port}/health/ready"
        )

    def run(self):
        
        print("[SYNC] Edge Sync Agent started.")
        print(
            f"[SYNC] Retry interval: "
            f"{self.retry_interval} seconds"
        )
        print(
            f"[SYNC] Subscriber readiness URL: "
            f"{self.health_url}"
        )

        while True:

            sync_attempt_total.inc()
            self.replay_worker.outbox.update_pending_metric()
            connected = self.mqtt_publisher.connect()

            if not connected:

                sync_connection_failure_total.inc()
                print(
                    "[SYNC] MQTT connection failed. "
                    f"Retrying in {self.retry_interval} seconds."
                )

                self.replay_worker.outbox.update_pending_metric()
                time.sleep(
                    self.retry_interval
                )
                continue
            
            print(
                    "[SYNC] MQTT connection established."
            )       
                 
            if not self.subscriber_is_ready():
        
                print(
                    "[SYNC] Subscriber is NOT READY. "
                    "Replay will not start."
                )

                print(
                    f"[SYNC] Waiting {self.retry_interval} seconds "
                    "before retrying."
                )

                self.mqtt_publisher.disconnect()

                time.sleep(
                    self.retry_interval
                )

                continue

            print(
                "[SYNC] Subscriber is READY. "
                "Starting replay."
            )
            
            replayed = self.replay_worker.replay()
            
            print(
                f"[SYNC] Replay cycle completed. "
                f"Messages replayed: {replayed}"
            )
            
            self.replay_worker.outbox.update_pending_metric()

            self.mqtt_publisher.disconnect()

            if replayed == 0:

                print(
                    "[SYNC] No pending telemetry."
                )

                print(
                    f"[SYNC] Next sync attempt in "
                    f"{self.retry_interval} seconds."
                )

            time.sleep(
                self.retry_interval
            )
    
    def subscriber_is_ready(self):
    
        print(
            f"[SYNC] Checking subscriber readiness: "
            f"{self.health_url}"
        )

        try:

            response = urllib.request.urlopen(
                self.health_url,
                timeout=2
            )

            if response.status == 200:

                print(
                    "[SYNC] Subscriber is READY."
                )

                return True

            print(
                f"[SYNC] Subscriber is NOT READY. "
                f"HTTP status: {response.status}"
            )

            return False

        except Exception as error:

            print(
                f"[SYNC] Subscriber readiness check failed: "
                f"{error}"
            )

            return False
    
