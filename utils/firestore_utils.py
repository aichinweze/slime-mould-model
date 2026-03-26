import logging

from google.cloud import firestore
from google.cloud.firestore_v1 import CollectionReference
from google.cloud.firestore_v1.base_document import BaseDocumentReference

from models.models import GraphRouteWeights, Metrics, time_format


def collection_exists(collection_ref: CollectionReference) -> bool:
    query = collection_ref.limit(1)
    result = query.get()

    if len(result) > 0:
        return True
    else:
        return False

def subcollection_exists_in(doc_ref: BaseDocumentReference) -> bool:
    return True if list(doc_ref.collections()) else False

def document_exists(document_ref: BaseDocumentReference) -> bool:
    doc = document_ref.get()
    doc_exists = doc.exists
    logging.debug(f"Checking if document exists in Metrics store: {doc_exists}: data: {doc.to_dict()}")

    if doc_exists:
        return True
    else:
        return False

def get_latest_graph_route_weights(firestore_client: firestore.Client) -> GraphRouteWeights:
    route_weight_ref = firestore_client.collection(u'route_weight')

    get_latest_route_weight_query = route_weight_ref.order_by(
        field_path="iteration",
        direction=firestore.Query.DESCENDING
    ).limit(1)

    result = get_latest_route_weight_query.get()[0]
    graph_route_weights = GraphRouteWeights.from_dict(result.to_dict())

    return graph_route_weights

def build_metrics_for_edges(edge_ids: list[str], metrics_ref: BaseDocumentReference) -> list[Metrics]:
    edge_latencies: list[Metrics] = []

    for edge_id in edge_ids:
        edge_ref = metrics_ref.collection(edge_id)

        if collection_exists(edge_ref):
            get_edge_latency_query = edge_ref.order_by(
                field_path="timestamp",
                direction=firestore.Query.DESCENDING
            ).limit(1)

            result = get_edge_latency_query.get()[0]
            edge_latencies.append(Metrics.from_dict(result.to_dict()))
        else:
            edge_latencies.append(Metrics(edge_id, 2, 1, ""))

    return edge_latencies

def get_historical_metrics(edge_ref: CollectionReference, window_size: int) -> list[Metrics]:
    historical_docs_query = edge_ref.order_by(
        field_path="timestamp",
        direction=firestore.Query.DESCENDING
    ).limit(window_size - 1)

    historical_docs = historical_docs_query.get()

    historical_metrics: list[Metrics] = []
    for doc in historical_docs:
        historical_metrics.append(Metrics.from_dict(doc.to_dict()))

    return historical_metrics

def get_route_weights_after_time(firestore_client: firestore.Client, start_time: str):
    start_time_formatted = start_time.strftime(time_format)
    route_weight_ref = firestore_client.collection(u'route_weight')

    route_weights_in_period = route_weight_ref.where(
        "timestamp", ">=", start_time_formatted
    ).order_by(
        field_path="iteration",
        direction=firestore.Query.ASCENDING
    ).get()

    graph_route_weights: list[GraphRouteWeights] = []

    for route_weights in route_weights_in_period:
        graph_route_weights.append(GraphRouteWeights.from_dict(route_weights.to_dict()))

    return graph_route_weights

def get_latency_at_timestamp(edge_ref: CollectionReference, timestamp: str):
    timestamp_formatted = timestamp.strftime(time_format)
    latest_edge_metrics = edge_ref.where(
        "timestamp", "<=", timestamp_formatted
    ).order_by(
        field_path="timestamp",
        direction=firestore.Query.DESCENDING
    ).limit(1)

    result = latest_edge_metrics.get()[0]
    metrics = Metrics.from_dict(result.to_dict())

    return metrics


