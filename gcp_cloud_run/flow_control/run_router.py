import base64

import functions_framework
from cloudevents.http import CloudEvent


@functions_framework.cloud_event
def process_message(event: CloudEvent) -> None:
    if event.data and "message" in event.data and "data" in event.data["message"]:
        base64_data = event.data["message"]["data"]
        message_detail = base64.b64decode(base64_data).decode("utf-8")
        print(message_detail)
    else:
        print("No message data received.")