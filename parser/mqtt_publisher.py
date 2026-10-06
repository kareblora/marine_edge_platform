import logging
import json
import paho.mqtt.client as mqtt

from .metrics import (
    mqtt_publisher_connection_status,
    mqtt_publisher_connection_failure_total,
    mqtt_publish_total,
    mqtt_publish_success_total,
    mqtt_publish_failure_total,
)

logger = logging.getLogger("MQTTPublisher")

class MQTTPublisher:

    def __init__(self, broker_host, broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port

        self.client = mqtt.Client(
            # mqtt.CallbackAPIVersion.VERSION2
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

    def connect(self):
        try:
            self.client.connect(
                self.broker_host,
                self.broker_port,
                60
            )

            self.client.loop_start()
            mqtt_publisher_connection_status.set(1)

            return True

        except Exception as error:
            mqtt_publisher_connection_status.set(0)
            mqtt_publisher_connection_failure_total.inc()
            logger.error("MQTT connection failed: %s", error)
            return False

    def publish(self, topic, payload):
        message = json.dumps(payload)
        
        mqtt_publish_total.inc()

        try:
            result = self.client.publish(
                topic,
                message,
                qos=1
            )

            result.wait_for_publish(
                timeout=5
            )
            
            if not result.is_published():
                mqtt_publish_failure_total.inc()
                return False

            mqtt_publish_success_total.inc()
            return True

        except Exception as error:

            logger.error("MQTT publish failed: %s", error)
            
            mqtt_publish_failure_total.inc()
            return False


    def disconnect(self):
        try:
            self.client.disconnect()
            self.client.loop_stop()
        
        finally:
            mqtt_publisher_connection_status.set(0)
