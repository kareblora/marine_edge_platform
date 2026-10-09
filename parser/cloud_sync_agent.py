import time
import logging
import json
import urllib.request
import urllib.error
import http.client

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import NoCredentialsError, BotoCoreError

logger = logging.getLogger("CloudSyncAgent")
client_logger = logging.getLogger("HTTPCloudClient")


class HTTPCloudClient:

    def __init__(self, endpoint, timeout=5, region="us-east-1"):
        self.endpoint = endpoint
        self.timeout = timeout
        self.region = region
        self.session = boto3.Session()
        self.credentials = self.session.get_credentials()

    def send(self, message_id, payload):

        client_logger.info(
            "Sending message %s to %s",
            message_id,
            self.endpoint,
        )

        data = json.dumps({
            "message_id": message_id,
            "payload": payload,
        }).encode("utf-8")

        if self.credentials is None:
            client_logger.error("No AWS credentials available for SigV4 signing")
            return False

        aws_request = AWSRequest(
            method="POST",
            url=self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": message_id,
            },
        )

        try:
            credentials = self.credentials.get_frozen_credentials()

            SigV4Auth(
                credentials,
                "execute-api",
                self.region,
            ).add_auth(aws_request)

            request = urllib.request.Request(
                self.endpoint,
                data=data,
                headers=dict(aws_request.headers.items()),
                method="POST",
            )

        except (NoCredentialsError, BotoCoreError):
            client_logger.exception("Unable to sign cloud API request")
            return False

        try:

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                status_code = response.status

                client_logger.info(
                    "Cloud API response for %s: HTTP %d",
                    message_id,
                    status_code,
                )

                return 200 <= status_code < 300

        except urllib.error.HTTPError as error:

            response_body = error.read().decode("utf-8", errors="replace")

            client_logger.error(
                    "Cloud API returned HTTP %d for message %s. Response: %s",
                error.code,
                message_id,
                response_body,
            )

            return False

        except urllib.error.URLError as error:

            client_logger.error(
                "Cloud API connection failed for message %s: %s",
                message_id,
                error,
            )

            return False

        except http.client.RemoteDisconnected:
            client_logger.error(
                "Cloud API disconnected before responding for message %s",
                message_id,
            )

            return False

        except TimeoutError:

            client_logger.error(
                "Cloud API request timed out for message %s",
                message_id,
            )

            return False

class CloudSyncAgent:

    def __init__(
        self,
        cloud_sync_worker,
        retry_interval=10,
    ):
        self.cloud_sync_worker = cloud_sync_worker
        self.retry_interval = retry_interval

    def run(self):

        logger.info("Cloud Sync Agent started.")
        logger.info("Retry interval: %s seconds", self.retry_interval)

        while True:

            self.cloud_sync_worker.outbox.update_cloud_pending_metric()
            
            synced = self.cloud_sync_worker.sync()
            
            self.cloud_sync_worker.outbox.update_cloud_pending_metric()

            logger.info("Sync cycle completed. Messages synchronized: %s", synced)

            time.sleep(
                self.retry_interval
            )
