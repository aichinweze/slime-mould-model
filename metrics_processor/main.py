import base64
import json
import os
import functions_framework
import logging
import google.cloud.logging

from datetime import datetime
from cloudevents.http import CloudEvent
from google.cloud import firestore

from utils.firestore_utils import collection_exists, get_historical_metrics
from utils.metrics_utils import aggregate_metrics
from models.models import CryptoResult, Metrics, time_format

PROJECT_ID = os.getenv("PROJECT_ID")
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE', 5))
DATABASE_ID = os.environ['DATABASE_ID']

@functions_framework.cloud_event
def update_metrics(cloud_event: CloudEvent):
    client = google.cloud.logging.Client(project=PROJECT_ID)
    client.setup_logging()

    logging.getLogger().setLevel(logging.DEBUG)

    if "message" in cloud_event.data and "data" in cloud_event.data["message"]:
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        parsed_data = json.loads(message_data) if message_data else {}

        firestore_client = firestore.Client(database=DATABASE_ID)

        crypto_result = CryptoResult.from_dict(parsed_data)
        edge_id = crypto_result.get_edge_id()
        execution_time = crypto_result.get_execution_time()

        metrics_ref = firestore_client.collection(u'metrics')
        edge_ref = metrics_ref.document("edge_metrics").collection(edge_id)
        timestamp = datetime.now().strftime(time_format)
        new_metric = Metrics(edge_id=edge_id, avg_latency=execution_time, document_count=1, timestamp=timestamp)
        new_metric_ref = edge_ref.document()

        if not collection_exists(edge_ref):
            new_metric_ref.set(new_metric.to_dict())
        else:
            historical_metrics = get_historical_metrics(edge_ref, WINDOW_SIZE)
            aggregated_metric_to_commit = aggregate_metrics(historical_metrics, new_metric)
            new_metric_ref.set(aggregated_metric_to_commit.to_dict())

        return f"Committed new metrics to edge {edge_id}"
    else:
        return "Data is not available in CloudEvent"

