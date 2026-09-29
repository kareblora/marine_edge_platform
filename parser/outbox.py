import json
import sqlite3


class TelemetryOutbox:

    def __init__(self, database_path):
        self.database_path = database_path

        self.connection = sqlite3.connect(
            self.database_path
        )

        self.create_table()

    def create_table(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS outbox (
                message_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)

        self.connection.commit()

    def add(self, message_id, topic, payload):
        self.connection.execute(
            """
            INSERT OR IGNORE INTO outbox (
                message_id,
                topic,
                payload
            )
            VALUES (?, ?, ?)
            """,
            (
                message_id,
                topic,
                json.dumps(payload)
            )
        )

        self.connection.commit()

    def mark_sent(self, message_id):
        self.connection.execute(
            """
            UPDATE outbox
            SET status = 'SENT'
            WHERE message_id = ?
            """,
            (message_id,)
        )

        self.connection.commit()

    def get_pending(self):
        cursor = self.connection.execute(
            """
            SELECT
                message_id,
                topic,
                payload,
                attempts
            FROM outbox
            WHERE status = 'PENDING'
            ORDER BY rowid
            """
        )

        return cursor.fetchall()

    def increment_attempts(self, message_id):
        self.connection.execute(
            """
            UPDATE outbox
            SET attempts = attempts + 1
            WHERE message_id = ?
            """,
            (message_id,)
        )

        self.connection.commit()

    def close(self):
        self.connection.close()