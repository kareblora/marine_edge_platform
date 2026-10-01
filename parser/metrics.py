from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import start_http_server


# MQTT
mqtt_connection_status = Gauge(
    "marine_mqtt_connection_status",
    "MQTT connection status: 1 connected, 0 disconnected"
)

mqtt_publish_total = Counter(
    "marine_mqtt_publish_total",
    "Total MQTT publish attempts"
)

mqtt_publish_success_total = Counter(
    "marine_mqtt_publish_success_total",
    "Total successful MQTT publishes"
)

mqtt_publish_failure_total = Counter(
    "marine_mqtt_publish_failure_total",
    "Total failed MQTT publishes"
)

mqtt_receive_total = Counter(
    "marine_mqtt_receive_total",
    "Total MQTT messages received"
)

mqtt_connection_failure_total = Counter(
    "marine_mqtt_connection_failure_total",
    "Total failed MQTT connection attempts"
)

# Telemetry persistence
telemetry_store_total = Counter(
    "marine_telemetry_store_total",
    "Total telemetry records successfully stored"
)

telemetry_store_failure_total = Counter(
    "marine_telemetry_store_failure_total",
    "Total telemetry storage failures"
)


# Outbox
outbox_pending_messages = Gauge(
    "marine_outbox_pending_messages",
    "Number of telemetry messages currently pending delivery"
)

outbox_messages_added_total = Counter(
    "marine_outbox_messages_added_total",
    "Total messages added to the outbox"
)


# Replay
replay_success_total = Counter(
    "marine_replay_success_total",
    "Total messages successfully replayed"
)

replay_failure_total = Counter(
    "marine_replay_failure_total",
    "Total replay failures"
)


# Sync Agent
sync_attempt_total = Counter(
    "marine_sync_attempt_total",
    "Total synchronization attempts"
)

sync_connection_failure_total = Counter(
    "marine_sync_connection_failure_total",
    "Total synchronization connection failures"
)


# Processing latency
telemetry_processing_seconds = Histogram(
    "marine_telemetry_processing_seconds",
    "Time spent processing a telemetry record"
)

def start_metrics_server(port):
    start_http_server(port)
    print(f"Prometheus metrics available on port {port}")