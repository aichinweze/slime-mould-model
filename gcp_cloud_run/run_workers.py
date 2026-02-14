import json

import functions_framework

import time

from .workers.worker_a import WorkerA
from .workers.worker_b import WorkerB
from .workers.worker_c import WorkerC

from google.cloud import pubsub_v1

import os

# TODO: Remove test values
PROJECT_ID = os.environ.get('PROJECT_ID', "testing-123")
PUBLISHER_SUCCESS_TOPIC_ID = os.environ.get('PUBLISHER_SUCCESS_TOPIC_ID')#, "worker-success-topic")
PUBLISHER_ERROR_TOPIC_ID = os.environ.get('PUBLISHER_ERROR_TOPIC_ID', "worker-error-topic")

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_SUCCESS_TOPIC_ID)
error_topic_path = publisher.topic_path(PROJECT_ID, PUBLISHER_ERROR_TOPIC_ID)

# Indicate which worker type is supposed to be used in this container
# TODO: Throw an error if this is not specified
worker_type = os.environ.get("WORKER_TYPE", "a")

@functions_framework.http
def process_routed_request(request):
    """
    HTTP Cloud Function:
    This function is triggered by the Router and implements the specified worker type (from environment variable).
    The request will come from the flow_control and contain information about the cryptocurrency pair to convert.
    """

    content_type = request.headers["content-type"]
    if content_type == "application/json":
        request_json = request.get_json(silent=True)
        if request_json and "source_currency" in request_json and "target_currency" in request_json:
            start_time = time.perf_counter()

            source_currency = request_json["source_currency"]
            target_currency = request_json["target_currency"]

            if worker_type == "a":
                worker = WorkerA(source_currency, target_currency)
                print("Using worker A")
                worker_out = worker.execute()
            elif worker_type == "b":
                worker = WorkerB(source_currency, target_currency)
                print("Using worker B")
                worker_out = worker.execute()
            else:
                worker = WorkerC(source_currency, target_currency)
                print("Using worker C")
                worker_out = worker.execute()

            end_time = time.perf_counter()

            execution_time = end_time - start_time

            worker_out["execution_time"] = execution_time

            # TODO: If success flag true - publish to success topic, otherwise publish to error topic

            json_payload = json.dumps(worker_out)
            data = json_payload.encode("utf-8")

            publish_result = publisher.publish(success_topic_path, data=data)

            message_id = publish_result.result()
            print(f'Message ID: {message_id} published to topic {PUBLISHER_SUCCESS_TOPIC_ID}')
            print(worker_out)

            return message_id
        else:
            raise ValueError("JSON is invalid, or missing a property (either source currency or target currency)")

    # Get source and target currency from P/S message
    return "A thing"

    # TODO: Write output to publishing topic
        # source_currency
        # target_currency
        # amount


# source_currency_a = "BTC"
# target_currency_a = "USD"
#
# source_currency_b = "ETH"
# target_currency_b = "USD"
#
# source_currency_c = "FET"
# target_currency_c = "USD"
#
# worker_a = WorkerA(source_currency=source_currency_a, target_currency=target_currency_a)
# worker_b = WorkerB(source_currency=source_currency_b, target_currency=target_currency_b, number_of_loops=5)
# worker_c = WorkerC(source_currency=source_currency_c, target_currency=target_currency_c)
#
# print("Worker A")
# worker_a_out = worker_a.execute()
#
# print("Worker B")
# worker_b_out = worker_b.execute()
#
# print("Worker C")
# worker_c_out = worker_c.execute()
