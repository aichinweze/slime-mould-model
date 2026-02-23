import json
import os
import random

from google.cloud import pubsub_v1

os.environ["PROJECT_ID"] = "testing-123"
os.environ['PUBLISHER_SUCCESS_TOPIC_ID'] = "worker-success-topic"
os.environ["PUBSUB_EMULATOR_HOST"]= "localhost:8085"

publisher = pubsub_v1.PublisherClient()

success_topic_path = publisher.topic_path(os.environ["PROJECT_ID"], os.environ["PUBLISHER_SUCCESS_TOPIC_ID"])

currencies = ["BTC", "RNDR", "TAO", "ICP", "FET", "ETH", "ADA"]

for _ in range(5):
    test_currencies = random.sample(currencies, 2)
    message = { "source_currency": test_currencies[0], "target_currency": test_currencies[1] }

    json_payload = json.dumps(message)
    data = json_payload.encode("utf-8")

    publish_result = publisher.publish(success_topic_path, data=data)

    message_id = publish_result.result()
    print(f'Message ID: {message_id} published to topic {os.environ["PUBLISHER_SUCCESS_TOPIC_ID"]}')

print("Finished publishing all messages to topic")