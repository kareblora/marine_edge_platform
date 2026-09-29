from parser.mqtt_subscriber import MQTTSubscriber
from parser.config import MarineConfig
from parser.storage import TelemetryStorage


config = MarineConfig("config/config.json")

mqtt_config = config.get_mqtt_config()

device_id = config.get("device_id")
dive_id = config.get("dive_id")

topic = (
    f"{mqtt_config['topic_prefix']}/"
    f"{device_id}/"
    f"{dive_id}"
)

storage = TelemetryStorage(
    "output/marine_edge.db"
)

subscriber = MQTTSubscriber(
    mqtt_config["broker_host"],
    mqtt_config["broker_port"],
    topic,
    storage
)

subscriber.start()
