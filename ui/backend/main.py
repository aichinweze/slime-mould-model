import datetime
import json
import math
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from google.cloud import pubsub_v1
from google.protobuf import timestamp_pb2
from pydantic import BaseModel


class Message(BaseModel):
    source_currency: str
    target_currency: str

class MessageBatch(BaseModel):
    messages: list[Message]

load_dotenv()

def get_required_env_var(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Required environment variable {key} not set")
    return value

PROJECT_ID: str = get_required_env_var("PROJECT_ID")
MAX_MESSAGES: int = int(get_required_env_var("MAX_MESSAGES"))
FLOW_CONTROL_URL: str = get_required_env_var("FLOW_CONTROL_URL")
INPUT_TOPIC_ID: str = get_required_env_var("INPUT_TOPIC_ID")

app = FastAPI()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, INPUT_TOPIC_ID)

def publish_messages(messages: list[Message]):
    count_published_messages = 0

    for message in messages:
        data_dict: dict = message.model_dump()
        json_payload = json.dumps(data_dict)
        data = json_payload.encode("utf-8")

        publish_result = publisher.publish(topic_path, data=data)
        message_id = publish_result.result()

        if message_id:
            count_published_messages += 1

    return {"published": count_published_messages}

def purge_subscription(project_id: str, subscription_id: str):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(now)

    subscriber.seek(
        request={"subscription": subscription_path, "time": timestamp}
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/run")
def run(message_batch: MessageBatch):
    number_of_messages = len(message_batch.messages)
    flow_ctrl_request_counts = math.ceil(float(number_of_messages) / MAX_MESSAGES)

    for _ in range(flow_ctrl_request_counts):
        response = requests.post(FLOW_CONTROL_URL)

    return publish_messages(message_batch.messages)
