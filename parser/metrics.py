from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import start_http_server


mqtt_publisher_connection_status = Gauge(
    "marine_mqtt_publisher_connection_status",
    "MQTT publisher connection status: 1 connected, 0 disconnected"
)

mqtt_subscriber_connection_status = Gauge(
    "marine_mqtt_subscriber_connection_status",
    "MQTT subscriber connection status: 1 connected, 0 disconnected"
)

mqtt_subscriber_ready = Gauge(
    "marine_mqtt_subscriber_ready",
    "MQTT subscriber ready to receive telemetry: 1 ready, 0 not ready"
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

mqtt_publisher_connection_failure_total = Counter(
    "marine_mqtt_publisher_connection_failure_total",
    "Total failed MQTT publisher connection attempts"
)

mqtt_subscriber_connection_failure_total = Counter(
    "marine_mqtt_subscriber_connection_failure_total",
    "Total failed MQTT subscriber connection attempts"
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

# Cloud agent
cloud_sync_success_total = Counter(
    "marine_cloud_sync_success_total",
    "Total number of telemetry messages successfully synchronized to the cloud"
)

cloud_sync_failure_total = Counter(
    "marine_cloud_sync_failure_total",
    "Total number of failed cloud synchronization attempts"
)


def start_metrics_server(port):
    start_http_server(port)
    print(f"Prometheus metrics available on port {port}")