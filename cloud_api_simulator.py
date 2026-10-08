import sqlite3
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("CloudAPISimulator")
response_loss_messages = set()
SIMULATE_RESPONSE_LOSS = True
DATABASE = "cloud_api.db"



def initialize_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            message_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def store_telemetry(message_id, payload):
    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO telemetry (message_id, payload)
            VALUES (?, ?)
            """,
            (message_id, payload),
        )

        connection.commit()

        return cursor.rowcount == 1

    finally:
        connection.close()

class CloudAPIHandler(BaseHTTPRequestHandler):



    def do_POST(self):

        if self.path != "/telemetry":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        try:
            request_data = json.loads(
                body.decode("utf-8")
            )

            message_id = request_data.get("message_id")

            stored = store_telemetry(
                message_id,
                request_data.get("payload"),
            )

            if stored:
                logger.info(
                    "Accepted telemetry message: %s",
                    message_id,
                )
            else:
                logger.warning(
                    "Duplicate telemetry message received: %s",
                    message_id,
                )


            if (SIMULATE_RESPONSE_LOSS 
                and stored 
                and message_id not in response_loss_messages
            ):
                response_loss_messages.add(message_id)

                logger.warning(
                    "Simulating lost response for message %s",
                    message_id,
                )

                self.close_connection = True
                return

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json",
            )
            self.end_headers()

            response = {
                "status": "accepted",
                "message_id": message_id,
            }

            try:
                self.wfile.write(
                    json.dumps(response).encode("utf-8")
                )
           
            except BrokenPipeError:
                logger.warning(
                    "Client disconnected before receiving response for message %s",
                    message_id,
                )

        except (json.JSONDecodeError, UnicodeDecodeError) as error:

            logger.error(
                "Invalid request payload: %s",
                error,
            )

            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        return


def run():

    initialize_database()
    logger.info("Cloud API database initialized: %s", DATABASE)

    server = HTTPServer(
        ("0.0.0.0", 8080),
        CloudAPIHandler,
    )

    logger.info(
        "Cloud API simulator listening on port 8080"
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        logger.info(
            "Stopping Cloud API simulator..."
        )

    finally:

        server.server_close()


if __name__ == "__main__":
    run()
