import asyncio
import os
from datetime import datetime

import functions_framework

from .db.firestore_utils import *
from .flow_control.flow_control_utils import *
from .flow_control.route_handler import make_route_weights, RouteHandler
from .flow_control.slime_mould.graph import SlimeMouldGraph
from .models.models import SlimeMouldParams, time_format
from .flow_control.slime_mould.slime_mould_model import SlimeMouldModel
from .models.models import Metrics, GraphRouteWeights

# TODO: Remove test values
TARGET_URL_A = os.getenv("TARGET_URL", "http://localhost:8081")
TARGET_URL_B = os.getenv("TARGET_URL", "http://localhost:8082")
TARGET_URL_C = os.getenv("TARGET_URL", "http://localhost:8083")

NUMBER_OF_WORKERS = int(os.getenv("NUMBER_OF_WORKERS", 3))
NUMBER_OF_NODES = int(os.getenv("NUMBER_OF_NODES", 5))

PROJECT_ID = os.getenv("PROJECT_ID", "testing-123")
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID", "subscription-testing-123")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", 50))

PUBLISHER_ERROR_TOPIC_ID = os.environ.get('PUBLISHER_ERROR_TOPIC_ID')

workers = [TARGET_URL_A, TARGET_URL_B, TARGET_URL_C]

edges_dict = { 0: [1, 2, 3], 1: [0, 4], 2: [0, 4], 3: [0, 4], 4: [1, 2, 3] }
source_nodes = [0]
sink_nodes = [4]

# TODO: TIDY THIS FILE
@functions_framework.http
def update_controller(request):
    firestore_client = firestore.Client()

    route_weight_ref = firestore_client.collection(u'route_weight')
    metrics_ref = firestore_client.collection(u'metrics').document("edge_metrics")

    # Initialise graph and model params
    graph = SlimeMouldGraph(edges_dict=edges_dict, source_nodes=source_nodes, sink_nodes=sink_nodes)
    model_params = SlimeMouldParams(alpha=0.013, mu=0.022, epsilon=0.3, d_max=1.75, d_min=1e-4)

    timestamp = datetime.now().strftime(time_format)

    # Get metrics from metrics table in Firestore database
    if subcollection_exists_in(metrics_ref):
        print("Metrics store information exists. Using to build efficiency matrix...")

        # Build efficiency matrix to use in updating conductivity matrix
        edge_ids = get_edge_ids_from_dict(edges_dict)
        edge_latencies: list[Metrics] = build_metrics_for_edges(edge_ids, metrics_ref)
        source_metrics_dict = get_source_entries_from_metrics(edge_latencies)

        print("Efficiency metrics: {}".format(source_metrics_dict))
        efficiency_matrix = build_matrix_from_edge_weights(source_metrics_dict)
    else:
        print("Metrics store contains no information, so no efficiency matrix could be created")
        efficiency_matrix = None

    # Get route weight from route weight table in Firestore database
    if not collection_exists(route_weight_ref):
        print("Route weight table does not exist. Using initial values...")
        iteration = 0
        model = SlimeMouldModel(model_params, graph)
    else:
        print("Route weight table exists in Firestore...")
        # Build conductivity matrix from latest entries
        graph_route_weights = get_latest_graph_route_weights(firestore_client)
        iteration = graph_route_weights.get_iteration() + 1
        route_weights = graph_route_weights.get_route_weights()

        source_cond_dict = get_source_entries_from_route_weight(route_weights)
        conductivity_matrix = build_matrix_from_edge_weights(source_cond_dict)

        # Get efficiency matrix from above
        model = SlimeMouldModel(model_params, graph, efficiency_matrix, conductivity_matrix)

    pressure, updated_conductivity_matrix = model.run_model()

    conductivity_to_workers: list[float] = updated_conductivity_matrix[0].tolist()
    route_weights_to_commit = make_route_weights(conductivity_to_workers)
    graph_route_weights_to_commit = GraphRouteWeights(route_weights_to_commit, iteration, timestamp)

    # Write out updated route weight to Firestore database (with time information)
    try:
        route_weight_doc_ref = route_weight_ref.document()
        print("Committing graph route weights to Firestore...")
        route_weight_doc_ref.set(graph_route_weights_to_commit.to_dict())
    except Exception as e:
        return f'Unable to complete write to Firestore: {e}', 500

    route_handler = RouteHandler(
        worker_routes=workers,
        project_id=PROJECT_ID,
        subscription_id=SUBSCRIPTION_ID,
        error_topic_id=PUBLISHER_ERROR_TOPIC_ID,
        max_messages=MAX_MESSAGES,
        firestore_client=firestore_client
    )
    asyncio.run(route_handler.execute())
    route_handler.close_subscriber()

    return "Is all over. Don't cry, don't beg."
