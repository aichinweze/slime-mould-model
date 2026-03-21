import asyncio
import os
import logging
import google.cloud.logging
import functions_framework
import google

from utils.firestore_utils import *
from utils.flow_control_utils import *
from router_handler import make_route_weights, RouteHandler
from slime_mould.slime_mould_model import SlimeMouldGraph, SlimeMouldModel
from models.models import SlimeMouldParams, time_format, Metrics, GraphRouteWeights

from datetime import datetime
from google.cloud import firestore

TARGET_URL_A = os.environ.get("TARGET_URL_A")
TARGET_URL_B = os.environ.get("TARGET_URL_B")
TARGET_URL_C = os.environ.get("TARGET_URL_C")

NUMBER_OF_WORKERS = int(os.getenv("NUMBER_OF_WORKERS", 3))
NUMBER_OF_NODES = int(os.getenv("NUMBER_OF_NODES", 5))

PROJECT_ID = os.getenv("PROJECT_ID")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", 50))
DATABASE_ID = os.getenv('DATABASE_ID')

INPUT_SUBSCRIPTION_ID = os.environ.get("INPUT_SUBSCRIPTION_ID")
PUBLISHER_ERROR_TOPIC_ID = os.environ.get('PUBLISHER_ERROR_TOPIC_ID')

workers = [TARGET_URL_A, TARGET_URL_B, TARGET_URL_C]

edges_dict = { 0: [1, 2, 3], 1: [0, 4], 2: [0, 4], 3: [0, 4], 4: [1, 2, 3] }
source_nodes = [0]
sink_nodes = [4]

@functions_framework.http
def run_flow_control(request):
    firestore_client = firestore.Client(database=DATABASE_ID)

    client = google.cloud.logging.Client(project=PROJECT_ID)
    client.setup_logging()

    logging.getLogger().setLevel(logging.DEBUG)

    route_handler = RouteHandler(
        worker_routes=workers,
        project_id=PROJECT_ID,
        subscription_id=INPUT_SUBSCRIPTION_ID,
        error_topic_id=PUBLISHER_ERROR_TOPIC_ID,
        max_messages=MAX_MESSAGES,
        firestore_client=firestore_client
    )

    route_weight_ref = firestore_client.collection(u'route_weight')
    metrics_ref = firestore_client.collection(u'metrics').document("edge_metrics")

    # Initialise graph and model params
    graph = SlimeMouldGraph(edges_dict=edges_dict, source_nodes=source_nodes, sink_nodes=sink_nodes)
    model_params = SlimeMouldParams(alpha=0.013, mu=0.022, epsilon=0.3, d_max=1.75, d_min=1e-4)

    timestamp = datetime.now().strftime(time_format)

    # Get metrics from metrics table in Firestore database
    if subcollection_exists_in(metrics_ref):
        logging.info("Metrics store information exists. Using to build efficiency matrix.")

        # Build efficiency matrix to use in updating conductivity matrix
        edge_ids = get_edge_ids_from_dict(edges_dict)
        edge_latencies: list[Metrics] = build_metrics_for_edges(edge_ids, metrics_ref)
        source_metrics_dict = get_source_metrics_dict(edge_latencies)

        logging.debug("Efficiency metrics: {}".format(source_metrics_dict))
        efficiency_matrix = build_matrix_from_source_conductivities(source_metrics_dict)
    else:
        logging.info("Metrics store contains no information, so no efficiency matrix could be created")
        efficiency_matrix = None

    # Get route weight from route weight table in Firestore database
    if not collection_exists(route_weight_ref):
        logging.info("Route weight table does not exist. Using initial values...")
        iteration = 0
        model = SlimeMouldModel(model_params, graph)
    else:
        logging.info("Route weight table exists in Firestore...")
        # Build conductivity matrix from latest entries
        graph_route_weights = get_latest_graph_route_weights(firestore_client)
        iteration = graph_route_weights.get_iteration() + 1
        route_weights = graph_route_weights.get_route_weights()

        source_cond_dict = get_route_conductivities_from_route_weight(route_weights)
        conductivity_matrix = build_matrix_from_source_conductivities(source_cond_dict)

        # Get efficiency matrix from above
        model = SlimeMouldModel(model_params, graph, efficiency_matrix, conductivity_matrix)

    pressure, updated_conductivity_matrix = model.run_model()

    conductivity_to_workers: list[float] = updated_conductivity_matrix[0].tolist()
    route_weights_to_commit = make_route_weights(conductivity_to_workers)
    graph_route_weights_to_commit = GraphRouteWeights(route_weights_to_commit, iteration, timestamp)

    # Write out updated route weight to Firestore database (with time information)
    try:
        route_weight_doc_ref = route_weight_ref.document()
        logging.info("Committing graph route weights to Firestore...")
        route_weight_doc_ref.set(graph_route_weights_to_commit.to_dict())
    except Exception as e:
        return f'Unable to complete write to Firestore: {e}', 500

    asyncio.run(route_handler.execute())
    route_handler.close_subscriber()

    return "Completed run_flow_control Cloud Run Function"
