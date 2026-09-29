import json
import paho.mqtt.client as mqtt


class MQTTSubscriber:

    def __init__(self, broker_host, broker_port, topic):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected to MQTT broker: {reason_code}")

        client.subscribe(
            self.topic,
            qos=1
        )

        print(f"Subscribed to: {self.topic}")

    def on_message(self, client, userdata, message):
        payload = json.loads(
            message.payload.decode("utf-8")
        )

        print(
            f"Received telemetry: "
            f"{payload.get('timestamp')}"
        )

    def start(self):
        self.client.connect(
            self.broker_host,
            self.broker_port,
            60
        )

        self.client.loop_forever()