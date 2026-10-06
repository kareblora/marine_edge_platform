import json
import sqlite3
import logging

logger = logging.getLogger("TelemetryStorage")

class TelemetryStorage:

    def __init__(self, database_path):
        self.database_path = database_path

        self.connection = sqlite3.connect(
            self.database_path,
            timeout=30
        )

        self.connection.execute(
            "PRAGMA journal_mode=WAL"
        )
        
        self.create_table()

    def create_table(self):
        try:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    timestamp TEXT,
                    device_id TEXT,
                    diver_id TEXT,
                    dive_id TEXT,
                    payload TEXT
                )
            """)

            self.connection.commit()

        except sqlite3.Error as error:
            logger.error(
                "Failed to initialize telemetry table: %s",
                error
            )
            raise

    def save(self, telemetry):
        try:
            self.connection.execute(
                """
                INSERT INTO telemetry (
                    message_id,
                    timestamp,
                    device_id,
                    diver_id,
                    dive_id,
                    payload
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    telemetry.get("message_id"),
                    telemetry.get("timestamp"),
                    telemetry.get("device_id"),
                    telemetry.get("diver_id"),
                    telemetry.get("dive_id"),
                    json.dumps(telemetry)
                )
            )

            self.connection.commit()
        
        except sqlite3.IntegrityError:
            logger.warning(
                "Telemetry with message_id %s already exists. Skipping.",
                telemetry.get("message_id")
            )
            
        except sqlite3.Error as error:
            logger.error(
                "Failed to save telemetry message %s: %s",
                telemetry.get("message_id"),
                error
            )
            raise

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()
