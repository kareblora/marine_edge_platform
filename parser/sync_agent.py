import logging
import time
import urllib.request

from .metrics import (
    sync_attempt_total,
    sync_connection_failure_total,
)

logger = logging.getLogger("EdgeSyncAgent")

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
        
        logger.info("Edge Sync Agent started.")
        logger.info("Retry interval: %s seconds", self.retry_interval)
        logger.info("Subscriber readiness URL: %s", self.health_url)

        while True:

            sync_attempt_total.inc()
            self.replay_worker.outbox.update_pending_metric()
            connected = self.mqtt_publisher.connect()

            if not connected:

                sync_connection_failure_total.inc()
                logger.warning("MQTT connection failed. Retrying in %s seconds.", self.retry_interval)

                self.replay_worker.outbox.update_pending_metric()
                time.sleep(
                    self.retry_interval
                )
                continue
            
            logger.info("MQTT connection established.")
                 
            if not self.subscriber_is_ready():
        
                logger.warning("Subscriber is NOT READY. Replay will not start.")

                logger.info("Waiting %s seconds before retrying.",
                    self.retry_interval
                )

                self.mqtt_publisher.disconnect()

                time.sleep(
                    self.retry_interval
                )

                continue

            logger.info("Subscriber is READY. Starting replay.")
            
            replayed = self.replay_worker.replay()
            
            logger.info("Replay cycle completed. Messages replayed: %s", replayed)
            
            self.replay_worker.outbox.update_pending_metric()

            self.mqtt_publisher.disconnect()

            if replayed == 0:

                logger.info("No pending telemetry.")

                logger.info("Next sync attempt in %s seconds.", self.retry_interval)

            time.sleep(
                self.retry_interval
            )
    
    def subscriber_is_ready(self):
    
        logger.info("Checking subscriber readiness: %s", self.health_url)

        try:

            response = urllib.request.urlopen(
                self.health_url,
                timeout=2
            )

            if response.status == 200:

                logger.info("Subscriber is READY.")

                return True

            logger.warning(
                "Subscriber is NOT READY. HTTP status: %s", response.status
            )

            return False

        except Exception as error:

            logger.error(
                "Subscriber readiness check failed: %s", error
            )

            return False
    
