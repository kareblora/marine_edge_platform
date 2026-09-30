from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.mqtt_publisher import MQTTPublisher
from parser.sync_agent import EdgeSyncAgent


config = MarineConfig(
    "config/config.json"
)

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

agent = EdgeSyncAgent(
    outbox,
    publisher,
    retry_interval
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