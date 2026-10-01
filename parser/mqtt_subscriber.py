import json
import paho.mqtt.client as mqtt

from .metrics import (
    mqtt_subscriber_connection_status,
    mqtt_receive_total,
    mqtt_subscriber_connection_failure_total,
    telemetry_store_total,
    telemetry_store_failure_total,
)

class MQTTSubscriber:

    def __init__(self, broker_host, broker_port, topic, storage):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.storage = storage

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        # Automatic MQTT reconnect backoff
        self.client.reconnect_delay_set(
            min_delay=1,
            max_delay=30
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.message_count = 0
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, reason_code, properties):
        
        if reason_code == 0:
            mqtt_subscriber_connection_status.set(1)
            print(f"Connected to MQTT broker: {reason_code}")

            client.subscribe(
                self.topic,
                qos=1
            )

            print(f"Subscribed to: {self.topic}")

    def on_message(self, client, userdata, message):
        mqtt_receive_total.inc()
        
        try:
            payload = json.loads(
                message.payload.decode("utf-8")
            )

            self.storage.save(payload)
            self.message_count += 1
            telemetry_store_total.inc()
            
            print(
                f"Received message #{self.message_count}"
            )

            print(
                f"Stored telemetry: "
                f"{payload.get('timestamp')}"
            )
        
        except Exception as e:
            telemetry_store_failure_total.inc()
            print(f"Failed to process telemetry: {e}")    

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        mqtt_subscriber_connection_status.set(0)

        print(f"MQTT disconnected: {reason_code}")

    def start(self):
        try:
            self.client.connect(
                self.broker_host,
                self.broker_port,
                60
            )

            self.client.loop_forever()

        except Exception as e:
            mqtt_subscriber_connection_failure_total.inc()

            print(f"MQTT connection failed: {e}")

    
    # def start(self):
        
    #     self.client.connect(
    #         self.broker_host,
    #         self.broker_port,
    #         60
    #     )

    #     self.client.loop_forever()
