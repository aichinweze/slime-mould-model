import json
import os
import random

from google.cloud import pubsub_v1

# Local development script. Requires the Pub/Sub and Firestore emulators to be running.
# See firebase.json for emulator configuration. Not intended for production use.

os.environ["PROJECT_ID"] = "testing-123"
os.environ['PUBLISHER_SUCCESS_TOPIC_ID'] = "worker-success-topic"
os.environ["PUBSUB_EMULATOR_HOST"]= "localhost:8085"

NUM_MESSAGES = int(os.getenv("NUM_MESSAGES", 5))

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(os.environ["PROJECT_ID"], os.environ["PUBLISHER_SUCCESS_TOPIC_ID"])

currencies = ["BTC", "RNDR", "TAO", "ICP", "FET", "ETH", "ADA"]

def create_test_data() -> list[dict]:
    messages = []
    for _ in range(NUM_MESSAGES):
        test_currencies = random.sample(currencies, 2)
        messages.append({"source_currency": test_currencies[0], "target_currency": test_currencies[1]})

    return messages

def manual_publish(test_data_dict: list[dict]):
    for data in test_data_dict:
        json_payload = json.dumps(data)
        data = json_payload.encode("utf-8")

        publish_result = publisher.publish(success_topic_path, data=data)

        message_id = publish_result.result()
        print(f'Message ID: {message_id} published to topic {os.environ["PUBLISHER_SUCCESS_TOPIC_ID"]}')



test_data = create_test_data()
manual_publish(test_data)

print("Finished publishing all messages to topic")