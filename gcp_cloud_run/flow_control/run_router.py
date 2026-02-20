import base64
import json
import random

import functions_framework
import requests
from cloudevents.http import CloudEvent

import os

TARGET_URL_A = os.getenv("TARGET_URL", "http://localhost:8080")
TARGET_URL_B = os.getenv("TARGET_URL", "http://localhost:8081")
TARGET_URL_C = os.getenv("TARGET_URL", "http://localhost:8082")

test_weights = [0.7, 0.23, 0.02]
workers = [TARGET_URL_A, TARGET_URL_B, TARGET_URL_C]

@functions_framework.cloud_event
def process_message(event: CloudEvent) -> None:
    if event.data and "message" in event.data and "data" in event.data["message"]:
        base64_data = event.data["message"]["data"]
        message_detail = base64.b64decode(base64_data).decode("utf-8")
        print(message_detail)

        selected_worker: str = random.choices(workers, weights=test_weights, k=1)[0]

        # TODO: Add proper authentication for how router calls workers --> IMPORTANT
        # Make the POST request
        try:
            response = requests.post(selected_worker, json=json.dumps(message_detail))#, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes (4XX or 5XX)
            return response.json() if response.content else response.text
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    else:
        print("No message data received.")
        return None