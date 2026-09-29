import json
import sqlite3


class TelemetryStorage:

    def __init__(self, database_path):
        self.database_path = database_path

        self.connection = sqlite3.connect(
            self.database_path
        )

        self.create_table()

    def create_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                device_id TEXT,
                diver_id TEXT,
                dive_id TEXT,
                payload TEXT
            )
        """)

        self.connection.commit()

    def save(self, telemetry):
        self.connection.execute(
            """
            INSERT INTO telemetry (
                timestamp,
                device_id,
                diver_id,
                dive_id,
                payload
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                telemetry.get("timestamp"),
                telemetry.get("device_id"),
                telemetry.get("diver_id"),
                telemetry.get("dive_id"),
                json.dumps(telemetry)
            )
        )

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()
