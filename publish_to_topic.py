import base64
import json
import os
import random

from google.cloud import pubsub_v1

crypto_codes = ["RNDR", "TAO", "ADA", "BTC", "ETH", "FET", "ICP", "LINK", "ONDO", "HBAR"]
currency = ["USD", "USDC"]

PROJECT_ID = os.getenv("PROJECT_ID")
NUM_MESSAGES = int(os.getenv("NUM_MESSAGES"))
TOPIC_TO_PUBLISH = os.getenv("TOPIC_TO_PUBLISH")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_TO_PUBLISH)

for _ in range(NUM_MESSAGES):
    data_dict: dict = { "source_currency": random.choice(crypto_codes), "target_currency": random.choice(currency) }
    json_payload = json.dumps(data_dict)
    data = json_payload.encode("utf-8")

    publish_result = publisher.publish(topic_path, data=data)
    message_id = publish_result.result()
    print(f'Message ID: {message_id} published to topic {TOPIC_TO_PUBLISH}')
