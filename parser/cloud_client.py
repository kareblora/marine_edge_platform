class LocalCloudClient:
    
    def send(self, message_id, payload):
        print(
            f"[CLOUD CLIENT] Sending message: "
            f"{message_id}"
        )

        return True