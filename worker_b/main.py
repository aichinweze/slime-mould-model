import json
import os
import functions_framework
import logging
import google.cloud.logging

from google.cloud import pubsub_v1

from workers.worker_b import WorkerB

PROJECT_ID = os.environ.get('PROJECT_ID')
PUBLISHER_SUCCESS_TOPIC_ID = os.environ.get('PUBLISHER_SUCCESS_TOPIC_ID')
PUBLISHER_ERROR_TOPIC_ID = os.environ.get('PUBLISHER_ERROR_TOPIC_ID')
NODE_ID = int(os.environ.get('NODE_ID', 2))

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_SUCCESS_TOPIC_ID)
error_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_ERROR_TOPIC_ID)

@functions_framework.http
def process_routed_request(request):
    """
    HTTP Cloud Function:
    This function is triggered by the Router and implements the specified worker type (from environment variable).
    The request will come from the route_handler and contain information about the cryptocurrency pair to convert.
    """

    client = google.cloud.logging.Client(project=PROJECT_ID)
    client.setup_logging()

    logging.getLogger().setLevel(logging.DEBUG)

    logging.debug("Worker B processing routed request...")
    logging.debug("Worker B: request: {}".format(request))

    content_type = request.headers["content-type"]
    if content_type == "application/json":
        request_json = request.get_json(silent=True)
        logging.debug("Worker B: Request JSON: {}".format(request_json))
        if request_json and "data" in request_json:
            source_currency = request_json["data"]["source_currency"]
            target_currency = request_json["data"]["target_currency"]
            send_timestamp: str = request_json["send_timestamp"]

            worker = WorkerB(NODE_ID, source_currency, target_currency, send_timestamp)
            worker_out = worker.execute()

            logging.debug("Worker B: worker_out: {}".format(worker_out))

            json_payload = json.dumps(worker_out)
            data = json_payload.encode("utf-8")

            topic_path = success_topic_path if worker_out["success_response"] else error_topic_path
            topic_id = PUBLISHER_SUCCESS_TOPIC_ID if worker_out["success_response"] else PUBLISHER_ERROR_TOPIC_ID
            publish_result = publisher.publish(topic_path, data=data)

            message_id = publish_result.result()
            logging.debug(f'Message ID: {message_id} published to topic {topic_id}')

            return message_id
        else:
            raise ValueError("JSON is invalid, or missing a property (either source currency or target currency)")
    return "Worker B completed processing request"

