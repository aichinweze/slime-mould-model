import base64
import json
import random
from collections import Counter

import requests
from google.api_core import retry
from google.cloud import pubsub_v1, firestore
from numpy.typing import NDArray

from ..db.firestore_utils import get_latest_graph_route_weights
from ..models.models import RouteWeight, GraphRouteWeights


# encoded = "eyJzb3VyY2VfY3VycmVuY3kiOiAiQlRDIiwgInRhcmdldF9jdXJyZW5jeSI6ICJJQ1AiLCAiY3VycmVuY3lfcGFpciI6ICJCVEMtSUNQIiwgInN1Y2Nlc3NfcmVzcG9uc2UiOiB0cnVlLCAicHJpY2UiOiAzMDcwMy4xMDEwMTMyMDIzMzMsICJlcnJvciI6IG51bGwsICJleGVjdXRpb25fdGltZSI6IDE2LjU0OTgyMzg5OTk4NjIyMn0="
#
# decoded = base64.b64decode(encoded)
#
# print(decoded.decode("utf-8"))
#
# encoded = "eyJzb3VyY2VfY3VycmVuY3kiOiAiQlRDQ0QiLCAidGFyZ2V0X2N1cnJlbmN5IjogIklDUCIsICJjdXJyZW5jeV9wYWlyIjogIkJUQ0NELUlDUCIsICJzdWNjZXNzX3Jlc3BvbnNlIjogZmFsc2UsICJwcmljZSI6IG51bGwsICJlcnJvciI6ICJmYWlsZWQgdG8gZ2V0IHJhdGUgZm9yIChCVENDRCwgVVNEKTogcnBjIGVycm9yOiBjb2RlID0gTm90Rm91bmQgZGVzYyA9IG5vdCBmb3VuZCIsICJleGVjdXRpb25fdGltZSI6IDE2LjUwMjkyMTYwMDEyNzU5M30="
#
# decoded = base64.b64decode(encoded)
#
# print(decoded.decode("utf-8"))
#
# to_encode = '{"source_currency": "RNDR", "target_currency": "USD" }'
# encoded = base64.b64encode(json.dumps(to_encode).encode("utf-8"))
# print("Encoded Value")
# print(encoded)
#
#
# items = ["a", "b", "c"]
# weights = [0.75, 0.18, 0.07]
#
# selected_list = []
# for _ in range(100):
#     selected_item = random.choices(items, weights=weights, k=1)
#     selected_list.append(selected_item[0])
#
# item_counts = Counter(selected_list)
# print(item_counts)
# print(type(selected_list[0]))
#
# print(len({1: "a", 2: "b", 3: "c"}))

# TODO: Simplify and sort out functions here
def get_worker_route_weights(
        worker_conductivities: list[float],
        source_node: int = 0,
        sink_node: int = 4
) -> list[float]:

    worker_weights = []

    for idx, value in enumerate(worker_conductivities):
        if idx != sink_node and idx != source_node:
            worker_weights.append((idx, value))

    sorted_weights = sorted(worker_weights)

    return [value for idx, value in sorted_weights]


def make_route_weights(
        worker_conductivities: list[float],
        edge_delimiter: str = ">>",
        source_node: int = 0,
        sink_node: int = 4
) -> list[RouteWeight]:
    route_weights: list[RouteWeight] = []

    for index, value in enumerate(worker_conductivities):
        if index != sink_node and index != source_node:
            edge_id = f'{source_node}{edge_delimiter}{index}'
            route_weight = RouteWeight(edge_id=edge_id, conductivity=value)
            route_weights.append(route_weight)

    return route_weights

def get_worker_weights(graph_route_weights: GraphRouteWeights, edge_delimiter: str = ">>") -> list[float]:
    route_weights = graph_route_weights.get_route_weights()

    worker_weights = []
    for route_weight in route_weights:
        nodes = route_weight.edge_id.split(edge_delimiter)
        destination_node = int(nodes[1])
        conductivity = route_weight.get_conductivity()
        worker_weights.append((destination_node, conductivity))

    sorted_weights = sorted(worker_weights)

    return [value for _, value in sorted_weights]


class RouteHandler:
    def __init__(self,
                 worker_routes: list[str],
                 project_id: str,
                 subscription_id: str,
                 max_messages: int,
                 firestore_client: firestore.Client,
    ):
        self.worker_routes = worker_routes
        self.project_id = project_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.max_messages = max_messages
        self.subscription_id = subscription_id
        self.firestore_client = firestore_client

    def select_worker_route(self):
        graph_route_weights = get_latest_graph_route_weights(self.firestore_client)
        worker_weights = get_worker_weights(graph_route_weights)

        print("worker_weights: {}".format(worker_weights))
        print("worker routes: {}".format(self.worker_routes))

        selected_route: str = random.choices(self.worker_routes, weights=worker_weights, k=1)[0]
        return selected_route

    def get_messages_from_topic(self):
        subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)

        messages = []

        try:
            # The subscriber pulls a specific number of messages.
            response = self.subscriber.pull(
                request={ "subscription": subscription_path, "max_messages": self.max_messages },
                # Use a retry policy to handle transient errors and timeouts
                retry=retry.Retry(deadline=300),
                timeout=30.0
            )
        except Exception as e:
            print(f"An error occurred during Pub/Sub pull: {e}")
            return []

        if not response.received_messages:
            print("No messages received in this pull request.")
            return []

        ack_ids = []
        for received_message in response.received_messages:
            data: dict = json.loads(received_message.message.data.decode("utf-8"))
            messages.append({"data": data }) # TODO: Do I need any attributes?
            ack_ids.append(received_message.ack_id)
            print(f"Received message: {data} of type: {type(data)}")

        return messages, ack_ids

    def close_subscriber(self):
        self.subscriber.close()

    def execute(self):
        # Read N messages from Pub/Sub topic
        print("Executing route handler")
        subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)

        # Read from topic and acknowledge messages
        messages_to_process, ack_ids = self.get_messages_from_topic()

        responses = []
        for msg in messages_to_process:
            # Call a Cloud Run function to process the message
            # TODO: Send requests asynchronously
            responses.append(requests.post(
                url=self.select_worker_route(),
                json=json.dumps(msg),
                headers={'Content-Type': 'application/json'}
            ).status_code)

        item_counts = Counter(responses)
        print("Responses: " + str(item_counts))

        # Acknowledges the received messages so they will not be sent again.
        if ack_ids:
            self.subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": ack_ids}
            )
            print(f"Received and acknowledged {len(ack_ids)} messages.")


