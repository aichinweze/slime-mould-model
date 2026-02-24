import base64
import json
import os
import random
import functions_framework
import requests

from google.cloud import firestore, pubsub_v1
from datetime import datetime, timezone

from .flow_control.flow_control_utils import *
from .flow_control.route_handler import get_worker_route_weights, make_route_weights, RouteHandler
from .flow_control.slime_mould.graph import SlimeMouldGraph
from .flow_control.slime_mould.params import SlimeMouldParams
from .flow_control.slime_mould.slime_mould_model import SlimeMouldModel

from .db.firestore_utils import *
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

test_weights = [0.7, 0.23, 0.02]
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

    docs_metrics = list(metrics_ref.collections())

    metrics_collections = []
    metrics_flag = False

    if docs_metrics:
        metrics_collections = docs_metrics
        metrics_flag = True
        print("Metrics collection --> {}".format(metrics_collections))
    else:
        print("Metrics collection not found")

    # Initialise graph and model params
    graph = SlimeMouldGraph(edges_dict=edges_dict, source_nodes=source_nodes, sink_nodes=sink_nodes)
    model_params = SlimeMouldParams(alpha=0.013, mu=0.022, epsilon=0.3, d_max=1.75, d_min=1e-4)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # TODO: Change latency to track time between request being sent and request being processed!!!!!
    # TODO: Deduplication strategy

    # Get metrics from metrics table in Firestore database
    if metrics_flag:
        # Build efficiency matrix to use in updating conductivity matrix
        edge_ids = get_edge_ids_from_dict(edges_dict)
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
                edge_latencies.append(Metrics(edge_id, 2.5, 1, ""))

        # for edge_id in edge_ids:
        #     edge_ref = metrics_ref.collection(edge_id)
        #     get_edge_latency_query = edge_ref.order_by(
        #         field_path="timestamp",
        #         direction=firestore.Query.DESCENDING
        #     ).limit(1)
        #
        #     result = get_edge_latency_query.get()[0]
        #     edge_latencies.append(Metrics.from_dict(result.to_dict()))

        source_metrics_dict = get_source_entries_from_metrics(edge_latencies)
        efficiency_matrix = build_matrix_from_edge_weights(source_metrics_dict)
        print("Efficiency matrix built...")
        print(efficiency_matrix)
    else:
        print("Metrics store contains no information, so no efficiency matrix could be created")
        efficiency_matrix = None

    # Get route weight from route weight table in Firestore database
    if collection_exists(route_weight_ref):
        print("Route weight table exists in Firestore...")
        # Build conductivity matrix from latest entries
        get_latest_route_weight_query = route_weight_ref.order_by(
            field_path="iteration",
            direction=firestore.Query.DESCENDING
        ).limit(1)

        result = get_latest_route_weight_query.get()[0]

        # print("Result from Query...")
        # print(result.to_dict())

        graph_route_weights = GraphRouteWeights.from_dict(result.to_dict())
        # print("Graph route weights created from result dictionary...")
        # print(graph_route_weights)
        # print(graph_route_weights.to_dict())
        # # route_weights = [RouteWeight.from_dict(doc.to_dict()) for doc in results]

        next_iteration = graph_route_weights.get_iteration() + 1
        route_weights = graph_route_weights.get_route_weights()

        source_cond_dict = get_source_entries_from_route_weight(route_weights)
        # print("Source conductivity dictionary --> {}".format(source_cond_dict))
        conductivity_matrix = build_matrix_from_edge_weights(source_cond_dict)

        # Get efficiency matrix from above
        model = SlimeMouldModel(
            slime_mould_params=model_params,
            slime_mould_graph=graph,
            efficiency_matrix=efficiency_matrix,
            conductivity_matrix=conductivity_matrix
        )

        pressure, updated_conductivity_matrix = model.run_model()

        print("Updated conductivity matrix...")
        print(updated_conductivity_matrix)

        conductivity_to_workers: list[float] = updated_conductivity_matrix[0].tolist()
        worker_weights: list[float] = get_worker_route_weights(conductivity_to_workers)
        # print("Workers route weights --> {}".format(worker_weights))

        route_weights_to_commit = make_route_weights(conductivity_to_workers)

        graph_route_weights_to_commit = GraphRouteWeights(
            route_weights=route_weights_to_commit,
            iteration=next_iteration,
            timestamp=timestamp
        )
    else:
        # Load initial conductivity to Firestore DB

        # Set worker weights to even probability
        # print("There is no route weight table in Firestore...")
        conductivity_to_workers = [0.0 if (i in source_nodes or i in sink_nodes) else 1.0 for i in range(NUMBER_OF_NODES)]

        worker_weights = get_worker_route_weights(conductivity_to_workers)

        print("Worker route weights --> {}".format(worker_weights))

        next_iteration = 0

        # Generate conductivities at iteration 1 and load to Firestore DB
        route_weights_to_commit = make_route_weights(conductivity_to_workers)
        graph_route_weights_to_commit = GraphRouteWeights(
            route_weights=route_weights_to_commit,
            iteration=next_iteration,
            timestamp=timestamp
        )

        try:
            route_weight_doc_ref = route_weight_ref.document()
            print("Committing graph route weights to Firestore...")
            print(graph_route_weights_to_commit.to_dict())
            route_weight_doc_ref.set(graph_route_weights_to_commit.to_dict())
        except Exception as e:
            return f'Unable to complete write to Firestore: {e}', 500

        model = SlimeMouldModel(
            slime_mould_params=model_params,
            slime_mould_graph=graph
        )

        pressure, updated_conductivity_matrix = model.run_model()

        next_iteration = 1

        conductivity_to_workers: list[float] = updated_conductivity_matrix[0].tolist()
        worker_weights: list[float] = get_worker_route_weights(conductivity_to_workers)
        print("Workers route weights --> {}".format(worker_weights))

        route_weights_to_commit = make_route_weights(conductivity_to_workers)

        graph_route_weights_to_commit = GraphRouteWeights(
            route_weights=route_weights_to_commit,
            iteration=next_iteration,
            timestamp=timestamp
        )

    # Write out updated route weight to Firestore database (with time information)
    try:
        route_weight_doc_ref = route_weight_ref.document()
        print("Committing graph route weights to Firestore...")
        print(graph_route_weights_to_commit.to_dict())

        route_weight_doc_ref.set(graph_route_weights_to_commit.to_dict())
    except Exception as e:
        return f'Unable to complete write to Firestore: {e}', 500

    # TODO: Calculate efficiency values combining latency and throughput

   # Run routing function
        # Read N messages from Pub/Sub topic
        # Route messages to workers
    route_handler = RouteHandler(workers, PROJECT_ID, SUBSCRIPTION_ID, MAX_MESSAGES, firestore_client)
    route_handler.execute()
    route_handler.close_subscriber()

    print("Completed processing...")

    if worker_weights is not None:
        print(worker_weights)
    else:
        print("No worker weights found.")

    return "Is all over. Don't cry, don't beg."
