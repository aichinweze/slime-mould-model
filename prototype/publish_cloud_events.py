import json
import os
import random
import time

import requests
import threading

from datetime import datetime

from cloudevents.http import CloudEvent
from google.cloud import pubsub_v1

from gcp_cloud_run.models.models import CryptoResult

os.environ["PROJECT_ID"] = "testing-123"
os.environ['PUBLISHER_SUCCESS_TOPIC_ID'] = "worker-success-topic"
os.environ["PUBSUB_EMULATOR_HOST"]= "localhost:8085"

TARGET_ADDRESS = os.getenv('TARGET_ADDRESS', "http://localhost:8089")
NUM_MESSAGES = int(os.getenv("NUM_MESSAGES", 10))

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(os.environ["PROJECT_ID"], os.environ["PUBLISHER_SUCCESS_TOPIC_ID"])

currencies = ["BTC", "RNDR", "TAO", "ICP", "FET", "ETH", "ADA"]
edge_ids = ["0>>1", "O>>2", "0>>3"]
avg_latencies = [1, 2, 3]

def create_test_data() -> list[dict]:
    messages = []
    for _ in range(NUM_MESSAGES):
        edge_id: str = random.choice(edge_ids)
        test_currencies = random.sample(currencies, 2)
        source_currency: str = test_currencies[0]
        target_currency: str = test_currencies[1]
        currency_pair = f"{source_currency}-{target_currency}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_time: float = random.choice(avg_latencies)

        result = CryptoResult(edge_id, source_currency, target_currency, currency_pair, True, timestamp, execution_time)
        messages.append(result.to_dict())

    return messages

# def request_task(url, json_data=None, headers=None):
#     """Function to make the actual request in a separate thread."""
#     try:
#         # Use requests.post or requests.get as needed
#         print("Sending data to url: {}".format(url))
#         requests.post(url, json=json.dumps(json_data), headers=headers)
#         # Note: Any exceptions raised here will be in the thread's context
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")


# def publish_cloud_events(test_data_dict: list[dict]):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     for data in test_data_dict:
#         cloud_event = CloudEvent({
#             "specversion": "1.0",
#             "id": "test-event-123",
#             "source": "//pubsub.googleapis.com/projects/testing-123/topics/worker-success-topic",
#             "type": "google.cloud.pubsub.topic.v1.messagePublished",
#             "time": timestamp,
#         }, {
#             "message": {
#                 "messageId": "msg-123",
#                 "publishTime": "2026-02-23T18:49:00Z",
#                 "data": data,
#                 "attributes": {}
#             }
#         })
#
#         # cloud_event_headers = {
#         #     'Content-Type': 'application/cloudevents+json',
#         #     'ce-id': cloud_event.get_attributes()["id"],
#         #     'ce-specversion': cloud_event.get_attributes()["specversion"],
#         #     'ce-source': cloud_event.get_attributes()["source"],
#         #     'ce-type': cloud_event.get_attributes()["type"],
#         #     'ce-time': cloud_event.get_attributes()["time"]
#         # }
#
#         print("sending data: {}".format(data))
#
#         thread = threading.Thread(target=request_task, args=(TARGET_ADDRESS, data, {'Content-Type': 'application/json'}))
#         thread.start()


def publish_cloud_events(test_data_dict: list[dict]):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for data in test_data_dict:
        print("sending data: {}".format(data))

        json_payload = json.dumps(data)
        data = json_payload.encode("utf-8")

        publish_result = publisher.publish(success_topic_path, data=data)

        message_id = publish_result.result()

        time.sleep(2)
        print(f'Message ID: {message_id} published to topic {os.environ["PUBLISHER_SUCCESS_TOPIC_ID"]}')



test_data = create_test_data()
publish_cloud_events(test_data)

print("Finished sending requests as cloud events")