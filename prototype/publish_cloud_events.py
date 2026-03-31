import json
import os
import random
import time

from datetime import datetime

from google.cloud import pubsub_v1

from models.models import CryptoResult

# Local development script. Requires the Pub/Sub and Firestore emulators to be running.
# See firebase.json for emulator configuration. Not intended for production use.

os.environ["PROJECT_ID"] = "testing-123"
os.environ['PUBLISHER_SUCCESS_TOPIC_ID'] = "worker-success-topic"
os.environ["PUBSUB_EMULATOR_HOST"]= "localhost:8085"

TARGET_ADDRESS = os.getenv('TARGET_ADDRESS', "http://localhost:8089")
NUM_MESSAGES = int(os.getenv("NUM_MESSAGES", 10))

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(os.environ["PROJECT_ID"], os.environ["PUBLISHER_SUCCESS_TOPIC_ID"])

currencies = ["BTC", "RNDR", "TAO", "ICP", "FET", "ETH", "ADA"]
edge_ids = ["0>>1", "0>>2", "0>>3"]
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


def publish_cloud_events(test_data_dict: list[dict]):
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