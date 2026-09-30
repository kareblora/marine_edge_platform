import json
import paho.mqtt.client as mqtt


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

            return True

        except Exception as error:
            print(f"MQTT connection failed: {error}")
            return False

    # def connect(self):
    #     self.client.connect(
    #         self.broker_host,
    #         self.broker_port,
    #         60
    #     )
        
    #     self.client.loop_start()

    def publish(self, topic, payload):
        message = json.dumps(payload)

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
                return False

            return True

        except Exception as error:

            print(
                f"MQTT publish failed: {error}"
            )

            return False
        
        
        #result = self.client.publish(
        #    topic,
        #    message,
        #    qos=1
        #)

        result.wait_for_publish(timeout=5)   

        return result.rc

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
