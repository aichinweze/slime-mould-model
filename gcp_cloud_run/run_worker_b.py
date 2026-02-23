import json
import os
import time

import functions_framework
from google.cloud import pubsub_v1

from .workers.worker_b import WorkerB
from .workers.worker_base import convert_crypto_result_to_dict

# TODO: Remove test values
PROJECT_ID = os.environ.get('PROJECT_ID')
PUBLISHER_SUCCESS_TOPIC_ID = os.environ.get('PUBLISHER_SUCCESS_TOPIC_ID')
PUBLISHER_ERROR_TOPIC_ID = os.environ.get('PUBLISHER_ERROR_TOPIC_ID')

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_SUCCESS_TOPIC_ID)
error_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_ERROR_TOPIC_ID)

# Indicate which worker type is supposed to be used in this container
# TODO: Throw an error if this is not specified
worker_type = os.environ.get("WORKER_TYPE")

@functions_framework.http
def process_routed_request(request):
    """
    HTTP Cloud Function:
    This function is triggered by the Router and implements the specified worker type (from environment variable).
    The request will come from the flow_control and contain information about the cryptocurrency pair to convert.
    """

    content_type = request.headers["content-type"]
    if content_type == "application/json":
        request_json = json.loads(request.get_json(silent=True))
        if request_json and "data" in request_json:
            source_currency = request_json["data"]["source_currency"]
            target_currency = request_json["data"]["target_currency"]

            start_time = time.perf_counter()

            worker = WorkerB(source_currency, target_currency)
            print("Using worker B")
            worker_out = worker.execute()

            end_time = time.perf_counter()

            execution_time = end_time - start_time

            if worker_out.success_response:
                topic_path = success_topic_path
                topic_id = PUBLISHER_SUCCESS_TOPIC_ID
            else:
                topic_path = error_topic_path
                topic_id = PUBLISHER_ERROR_TOPIC_ID

            worker_message = convert_crypto_result_to_dict(worker_out)

            worker_message["execution_time"] = execution_time

            json_payload = json.dumps(worker_message)
            data = json_payload.encode("utf-8")

            publish_result = publisher.publish(topic_path, data=data)

            message_id = publish_result.result()
            print(f'Message ID: {message_id} published to topic {topic_id}')

            return message_id
        else:
            raise ValueError("JSON is invalid, or missing a property (either source currency or target currency)")

    # Get source and target currency from P/S message
    return "A thing"

