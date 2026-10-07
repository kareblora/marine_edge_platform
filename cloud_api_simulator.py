import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("CloudAPISimulator")


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

            logger.info(
                "Received telemetry message: %s",
                message_id,
            )

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

            self.wfile.write(
                json.dumps(response).encode("utf-8")
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