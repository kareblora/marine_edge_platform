from parser.mqtt_subscriber import MQTTSubscriber
from parser.config import MarineConfig
from parser.storage import TelemetryStorage
from parser.metrics import start_metrics_server

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from parser.metrics import mqtt_subscriber_ready

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

readiness_server = HTTPServer(
    ("0.0.0.0", 8081),
    ReadinessHandler
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

try:
    subscriber.start()

except KeyboardInterrupt:
    print("Stopping subscriber...")

finally:
    storage.close()
    print("Database connection closed.")
