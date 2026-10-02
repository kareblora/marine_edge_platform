from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.mqtt_publisher import MQTTPublisher
from parser.sync_agent import EdgeSyncAgent
from parser.replay_worker import ReplayWorker
from parser.metrics import start_metrics_server

start_metrics_server(8003)

config = MarineConfig("config/config.json")

subscriber_config = config.get_subscriber_config()

health_host = subscriber_config["health_host"]
health_port = subscriber_config["health_port"]

publisher_database = (
    config.get_publisher_database()
)

mqtt_config = config.get_mqtt_config()

retry_interval = (
    config.get_retry_interval()
)

outbox = TelemetryOutbox(
    publisher_database
)

publisher = MQTTPublisher(
    mqtt_config["broker_host"],
    mqtt_config["broker_port"]
)

replay_worker = ReplayWorker(
    outbox,
    publisher
)

agent = EdgeSyncAgent(
    replay_worker,
    publisher,
    retry_interval,
    health_host,
    health_port
)

try:

    agent.run()

except KeyboardInterrupt:

    print(
        "Stopping Edge Sync Agent..."
    )

finally:

    publisher.disconnect()
    outbox.close()

    print(
        "Edge Sync Agent stopped."
    )