import json
import logging
from pathlib import Path

logger = logging.getLogger("MarineConfig")

class MarineConfig:

    REQUIRED_FIELDS = [
        "device_id",
        "diver_id",
        "dive_id"
    ]

    def __init__(self, filename):
        self.filename = Path(filename)
        self.config = self._load()

    def _load(self):
        
        try:
            if not self.filename.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {self.filename}"
                )

            with open(self.filename) as f:
                config = json.load(f)

            self._validate(config)

            return config

        except FileNotFoundError as error:
            logger.error(
                "Configuration file not found: %s",
                error
            )
            raise

        except json.JSONDecodeError as error:
            logger.error(
                "Invalid JSON in configuration file %s: %s",
                self.filename,
                error
            )
            raise

        except ValueError as error:
            logger.error(
                "Configuration validation failed: %s",
                error
            )
            raise


    def _validate(self, config):

        for field in self.REQUIRED_FIELDS:

            if field not in config:
                raise ValueError(
                    f"Missing required configuration field: {field}"
                )

            if not config[field]:
                raise ValueError(
                    f"Configuration field cannot be empty: {field}"
                )

    def get(self, field):
        return self.config[field]

    def get_mqtt_config(self):
        return self.config["mqtt"]

    def get_publisher_database(self):
        return self.config["storage"]["publisher_database"]

    def get_telemetry_database(self):
        return self.config["storage"]["telemetry_database"]
    
    def get_retry_interval(self):
        return self.config["mqtt"]["retry_interval_seconds"]
    
    def get_subscriber_config(self):
        return self.config["subscriber"]
    
    def get_cloud_config(self):
        return self.config["cloud"]