import json
import sqlite3
import logging

from .metrics import (
    outbox_messages_added_total,
    outbox_pending_messages,
    cloud_pending_messages,
)

logger = logging.getLogger("TelemetryOutbox")

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
        try:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS outbox (
                    message_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    local_status TEXT NOT NULL DEFAULT 'PENDING',
                    cloud_status TEXT NOT NULL DEFAULT 'PENDING',
                    local_attempts INTEGER NOT NULL DEFAULT 0,
                    cloud_attempts INTEGER NOT NULL DEFAULT 0
                )
            """)

            self.connection.commit()
            
        except sqlite3.Error as error:
            logger.error(
                "Failed to initialize outbox table: %s", 
                error
            )
            raise

    def add(self, message_id, topic, payload):
        try:
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
            
        except sqlite3.Error as error:
            logger.error(
                "Failed to add message to outbox: %s", 
                error
            )
            raise
        
    def mark_sent(self, message_id):
        try:
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
        
        except sqlite3.Error as error:
            logger.error(
                "Failed to mark message %s as locally sent: %s", 
                message_id, 
                error
            )
            raise

    def increment_local_attempts(self, message_id):
        try:
            self.connection.execute(
                """
                UPDATE outbox
                SET local_attempts = local_attempts + 1
                WHERE message_id = ?
                """,
                (message_id,)
            )

            self.connection.commit()
            
        except sqlite3.Error as error:
            logger.error(
                "Failed to increment local attempts for message %s: %s",
                message_id,
                error
            )
            raise

    def get_pending(self, limit=100):
        cursor = self.connection.execute(
            """
            SELECT
                message_id,
                topic,
                payload,
                local_attempts
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
        
    def get_cloud_pending(self, limit=100):
        cursor = self.connection.execute(
            """
            SELECT
                message_id,
                payload,
                cloud_attempts
            FROM outbox
            WHERE cloud_status = 'PENDING'
            ORDER BY rowid
            LIMIT ?
            """,
            (limit,)
        )

        return cursor.fetchall()

    def mark_cloud_sent(self, message_id):
        try:
            self.connection.execute(
                """
                UPDATE outbox
                SET cloud_status = 'SENT'
                WHERE message_id = ?
                """,
            (message_id,)
            )

            self.connection.commit()

        except sqlite3.Error as error:
            logger.error(
                "Failed to mark message %s as cloud sent: %s", 
                message_id, 
                error
            )
            raise

    def increment_cloud_attempts(self, message_id):
        try:
            self.connection.execute(
                """
                UPDATE outbox
                SET cloud_attempts = cloud_attempts + 1
            WHERE message_id = ?
            """,
            (message_id,)
            )

            self.connection.commit()

        except sqlite3.Error as error:
            logger.error(
                "Failed to increment cloud attempts for message %s: %s", 
                message_id, 
                error
            )
            raise

    def get_cloud_pending_count(self):
        cursor = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM outbox
            WHERE cloud_status = 'PENDING'
            """
        )

        return cursor.fetchone()[0]
    
    def update_cloud_pending_metric(self):
        cloud_pending_messages.set(
            self.get_cloud_pending_count()
        )