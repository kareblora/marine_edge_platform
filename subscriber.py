from parser.mqtt_subscriber import MQTTSubscriber
from parser.config import MarineConfig
from parser.storage import TelemetryStorage
from parser.metrics import (
    start_metrics_server,
    mqtt_subscriber_ready,
)

from http.server import BaseHTTPRequestHandler, HTTPServer

import threading


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

print("[SUBSCRIBER] Starting Marine Edge MQTT Subscriber...")
print(
    f"[SUBSCRIBER] MQTT broker: "
    f"{mqtt_config['broker_host']}:{mqtt_config['broker_port']}"
)
print(
    f"[SUBSCRIBER] MQTT topic: {topic}"
)
print(
    f"[SUBSCRIBER] Telemetry database: "
    f"{telemetry_database}"
)

readiness_server = HTTPServer(
    ("0.0.0.0", 8081),
    ReadinessHandler
)

print(
    "[SUBSCRIBER] Readiness endpoint: "
    "http://0.0.0.0:8081/health/ready"
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

print("[SUBSCRIBER] Starting MQTT subscriber...")

try:
    subscriber.start()

except KeyboardInterrupt:
    print("Stopping subscriber...")

finally:

    print("[SUBSCRIBER] Shutting down readiness server...")
    readiness_server.shutdown()

    storage.close()

    print("[SUBSCRIBER] Database connection closed.")

