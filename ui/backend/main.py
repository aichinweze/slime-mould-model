import json
import math
import os
import time

import requests

from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import pubsub_v1
from google.protobuf import timestamp_pb2
from google.cloud import firestore
from pydantic import BaseModel

from models.models import time_format
from utils.firestore_utils import get_route_weights_after_time, get_latency_at_timestamp


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
INPUT_SUBSCRIPTION_ID: str = get_required_env_var("INPUT_SUBSCRIPTION_ID")
DATABASE_ID: str = get_required_env_var("DATABASE_ID")

WORKER_EDGE_IDS = ["0>>1", "0>>2", "0>>3"]

app = FastAPI()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, INPUT_TOPIC_ID)

firestore_client = firestore.Client(database=DATABASE_ID)
metrics_ref = firestore_client.collection(u'metrics')

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

def purge_subscription(project_id: str, subscription_id: str, start_time: datetime):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(start_time)

    subscriber.seek(
        request = { "subscription": subscription_path, "time": timestamp }
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/publish")
def publish(message_batch: MessageBatch):
    start_time = datetime.now(timezone.utc)

    purge_subscription(PROJECT_ID, INPUT_SUBSCRIPTION_ID, start_time)

    result = publish_messages(message_batch.messages)

    return {
        "published": result["published"],
        "start_time": start_time.strftime(time_format)
    }


@app.post("/api/run")
def run(batch_size: int):
    flow_ctrl_request_counts = math.ceil(float(batch_size) / MAX_MESSAGES)

    for _ in range(flow_ctrl_request_counts):
        response = requests.post(FLOW_CONTROL_URL)

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Flow control request failed with status code {response.status_code}"
            )

        time.sleep(5)

    return {
        "flow_control_invocations": flow_ctrl_request_counts,
    }

@app.get("/api/results")
def get_results(start_time: str):
    graph_weights_in_period = get_route_weights_after_time(firestore_client, start_time)

    edge_latency_history = []
    route_weight_history = []

    for graph_weight in graph_weights_in_period:
        # Handling route weight information for the iteration
        iteration = graph_weight.iteration
        iteration_timestamp = graph_weight.timestamp
        weights = []

        for weight in graph_weight.route_weights:
            edge_id = weight.edge_id
            conductivity = weight.conductivity
            weights.append({ "edge_id": edge_id, "conductivity": conductivity })

        route_weight_history.append({
            "iteration": iteration,
            "timestamp": iteration_timestamp,
            "weights": weights
        })

        # Handling edge latency information for the iteration
        iteration_latency_metrics = []

        for edge_id in WORKER_EDGE_IDS:
            edge_ref = metrics_ref.document("edge_metrics").collection(edge_id)
            iteration_metric = get_latency_at_timestamp(edge_ref, iteration_timestamp)

            if iteration_metric is not None:
                metric_dict = { "edge_id": edge_id, "avg_latency": iteration_metric.avg_latency }
                iteration_latency_metrics.append(metric_dict)
            else:
                break

        if len(iteration_latency_metrics) == len(WORKER_EDGE_IDS):
            edge_latency_history.append({
                "iteration": iteration,
                "latencies": iteration_latency_metrics
            })

    return {
        "route_weight_history": route_weight_history,
        "edge_latency_history": edge_latency_history
    }