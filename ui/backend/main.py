import json
import logging
import math
import os
import queue
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.cloud import firestore
from google.cloud import pubsub_v1
from google.protobuf import timestamp_pb2
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

MESSAGE_PULL_SIZE: int = int(get_required_env_var("MESSAGE_PULL_SIZE"))
MAX_MESSAGES: int = int(get_required_env_var("MAX_MESSAGES"))

FLOW_CONTROL_URL: str = get_required_env_var("FLOW_CONTROL_URL")

INPUT_TOPIC_ID: str = get_required_env_var("INPUT_TOPIC_ID")
INPUT_SUBSCRIPTION_ID: str = get_required_env_var("INPUT_SUBSCRIPTION_ID")
SUCCESS_TOPIC_SUBSCRIPTION_ID: str = get_required_env_var("SUCCESS_TOPIC_SUBSCRIPTION_ID")
ERROR_TOPIC_SUBSCRIPTION_ID: str = get_required_env_var("ERROR_TOPIC_SUBSCRIPTION_ID")

DATABASE_ID: str = get_required_env_var("DATABASE_ID")

WORKER_EDGE_IDS = ["0>>1", "0>>2", "0>>3"]

app = FastAPI()
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(PROJECT_ID, INPUT_TOPIC_ID)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger(__name__).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

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


def get_messages_from_topic(start_time: str, batch_size: int) -> list[dict]:
    start_time_dt = datetime.strptime(start_time, time_format).replace(tzinfo=timezone.utc)
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(start_time_dt)

    message_queue = queue.Queue()
    messages: list[dict] = []

    flow_control = pubsub_v1.types.FlowControl(max_messages=MESSAGE_PULL_SIZE)

    def callback(message):
        message_queue.put(json.loads(message.data.decode("utf-8")))
        message.ack()

    error_subscription_path = subscriber.subscription_path(PROJECT_ID, ERROR_TOPIC_SUBSCRIPTION_ID)
    success_subscription_path = subscriber.subscription_path(PROJECT_ID, SUCCESS_TOPIC_SUBSCRIPTION_ID)

    subscriber.seek(request={"subscription": error_subscription_path, "time": timestamp})
    subscriber.seek(request={"subscription": success_subscription_path, "time": timestamp})

    streaming_pull_future_success = subscriber.subscribe(
        success_subscription_path,
        callback=callback,
        flow_control=flow_control
    )

    streaming_pull_future_failure = subscriber.subscribe(
        error_subscription_path,
        callback=callback,
        flow_control=flow_control
    )

    attempt_count = 1
    quarter_mark = math.ceil(batch_size / 4)
    halfway_mark = math.ceil(batch_size / 2)
    threequarter_mark = math.ceil((3*batch_size) / 4)

    while len(messages) < batch_size:
        try:
            message = message_queue.get(timeout=10)
            messages.append(message)
            attempt_count = 1

            if len(messages) == quarter_mark:
                logging.debug(f"Retrieved approximately 25% of messages: {len(messages)}/{batch_size}")
            elif len(messages) == halfway_mark:
                logging.debug(f"Retrieved approximately 50% of messages: {len(messages)}/{batch_size}")
            elif len(messages) == threequarter_mark:
                logging.debug(f"Retrieved approximately 75% of messages: {len(messages)}/{batch_size}")
        except queue.Empty:
            logging.warning("Timeout while waiting for messages in message queue. Retry attempt: {}".format(attempt_count))
            if attempt_count <= 3:
                attempt_count += 1
                continue
            else:
                break

    streaming_pull_future_success.cancel()
    streaming_pull_future_failure.cancel()

    logging.info(f"Received and acknowledged {len(messages)} messages.")

    return messages


def purge_subscription(project_id: str, subscription_id: str, start_time: datetime):
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
    logger.info("publish: Received POST at /api/publish endpoint.")
    start_time = datetime.now(timezone.utc)

    purge_subscription(PROJECT_ID, INPUT_SUBSCRIPTION_ID, start_time)

    result = publish_messages(message_batch.messages)

    logger.info("publish: Completed request at /api/publish endpoint.")

    return {
        "published": result["published"],
        "start_time": start_time.strftime(time_format)
    }


@app.post("/api/run")
def run(batch_size: int):
    logger.info("run: Received POST at /api/run endpoint.")
    flow_ctrl_request_counts = math.ceil(float(batch_size) / MAX_MESSAGES)

    for i in range(flow_ctrl_request_counts):
        response = requests.post(FLOW_CONTROL_URL)

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Flow control request failed with status code {response.status_code}"
            )

        logger.debug(f"run: Completed {i + 1}/{flow_ctrl_request_counts} Flow control cycles")
        time.sleep(0.15)

    logger.info("run: Completed Flow Control cycles at /api/run endpoint.")

    return {
        "flow_control_invocations": flow_ctrl_request_counts,
    }

@app.get("/api/results")
def get_firestore_results(start_time: str):
    logger.info("get_firestore_results: Received GET at /api/results endpoint.")
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

    logger.info("get_firestore_results: Completed request at /api/results endpoint.")

    return {
        "route_weight_history": route_weight_history,
        "edge_latency_history": edge_latency_history
    }

@app.get("/api/message-counts")
def get_message_counts(start_time: str, batch_size: int):
    logger.info("get_message_counts: Received GET at /api/message-counts endpoint.")
    messages = get_messages_from_topic(start_time, batch_size)

    grouped_messages: dict = defaultdict(list)
    for message in messages:
        edge_id = message["edge_id"]
        key = edge_id if edge_id != "" else "N_A"
        success_response: bool = message["success_response"]
        grouped_messages[key].append(success_response)

    message_counts: list[dict] = []
    for key, grouped_msg in grouped_messages.items():
        message_counts.append({
            "edge_id": key,
            "success": grouped_msg.count(True),
            "error": grouped_msg.count(False)
        })

    logger.info("get_message_counts: Completed request at /api/message-counts endpoint.")

    return {
        "message_counts": message_counts,
    }