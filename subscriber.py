import logging
import threading

from parser.logging_config import configure_logging
from parser.mqtt_subscriber import MQTTSubscriber
from parser.config import MarineConfig
from parser.storage import TelemetryStorage
from parser.metrics import (
    start_metrics_server,
    mqtt_subscriber_ready,
)

from http.server import BaseHTTPRequestHandler, HTTPServer



configure_logging()

logger = logging.getLogger("SubscriberBootstrap")

class ReadinessHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/health/ready":

            if mqtt_subscriber_ready._value.get() == 1:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"READY")
            else:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"NOT READY")

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

start_metrics_server(8002)

config = MarineConfig("config/config.json")

mqtt_config = config.get_mqtt_config()

device_id = config.get("device_id")
dive_id = config.get("dive_id")

topic = (
    f"{mqtt_config['topic_prefix']}/"
    f"{device_id}/"
    f"{dive_id}"
)

telemetry_database = config.get_telemetry_database()

storage = TelemetryStorage(
    telemetry_database
)

logger.info("Starting Marine Edge MQTT Subscriber...")
logger.info(
    "MQTT broker: %s:%s", mqtt_config['broker_host'], mqtt_config['broker_port']
)
logger.info("MQTT topic: %s", topic)
logger.info(
    "Telemetry database: %s", telemetry_database
)

readiness_server = HTTPServer(
    ("0.0.0.0", 8081),
    ReadinessHandler
)

logger.info(
    "Readiness endpoint: http://0.0.0.0:8081/health/ready"
)

threading.Thread(
    target=readiness_server.serve_forever,
    daemon=True
).start()

subscriber = MQTTSubscriber(
    mqtt_config["broker_host"],
    mqtt_config["broker_port"],
    topic,
    storage
)

logger.info("Starting MQTT subscriber...")

try:
    subscriber.start()

except KeyboardInterrupt:
    logger.info("Stopping subscriber...")

finally:

    logger.info("Shutting down readiness server...")
    readiness_server.shutdown()

    storage.close()

    logger.info("Database connection closed.")

