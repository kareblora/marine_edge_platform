from parser.config import MarineConfig
from parser.outbox import TelemetryOutbox
from parser.mqtt_publisher import MQTTPublisher
from parser.replay_worker import ReplayWorker


config = MarineConfig(
    "config/config.json"
)

mqtt_config = config.get_mqtt_config()

publisher_database = (
    config.get_publisher_database()
)

outbox = TelemetryOutbox(
    publisher_database
)

publisher = MQTTPublisher(
    mqtt_config["broker_host"],
    mqtt_config["broker_port"]
)

connected = publisher.connect()

if not connected:
    print(
        "MQTT unavailable. "
        "Replay aborted."
    )

    outbox.close()
    exit(1)


worker = ReplayWorker(
    outbox,
    publisher
)

try:
    worker.replay()

finally:
    publisher.disconnect()
    outbox.close()