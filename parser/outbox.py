import json
import sqlite3

from .metrics import (
    outbox_messages_added_total,
    outbox_pending_messages,
)

class TelemetryOutbox:

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
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS outbox (
                message_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                local_status TEXT NOT NULL DEFAULT 'PENDING',
                cloud_status TEXT NOT NULL DEFAULT 'PENDING',
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
                payload,
                local_status,
                cloud_status
            )
            VALUES (?, ?, ?, 'PENDING', 'PENDING')
            """,
            (
                message_id,
                topic,
                json.dumps(payload)
            )
        )

        self.connection.commit()
        outbox_messages_added_total.inc()
        self.update_pending_metric()

    def mark_sent(self, message_id):
        self.connection.execute(
            """
            UPDATE outbox
            SET local_status = 'SENT'
            WHERE message_id = ?
            """,
            (message_id,)
        )

        self.connection.commit()
        self.update_pending_metric()

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

    def get_pending(self, limit=100):
        cursor = self.connection.execute(
            """
            SELECT
                message_id,
                topic,
                payload,
                attempts
            FROM outbox
            WHERE local_status = 'PENDING'
            ORDER BY rowid
            LIMIT ?
            """,
            (limit,)
        )

        return cursor.fetchall()

    def close(self):
        self.connection.close()
        
    def get_pending_count(self):
        cursor = self.connection.execute(
        "SELECT COUNT(*) FROM outbox WHERE local_status = 'PENDING'"
    )

        return cursor.fetchone()[0]

    def update_pending_metric(self):
        outbox_pending_messages.set(
            self.get_pending_count()
        )
        
