import base64
import json
import random
from collections import Counter

from numpy.typing import NDArray

from ..models.models import RouteWeight

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


class RouteHandler:
    def __init__(self, worker_routes: list[str], worker_weights: list[float]):
        self.worker_routes = worker_routes
        self.worker_weights = worker_weights

    def select_worker_route(self):
        selected_route: str = random.choices(self.worker_routes, weights=self.worker_weights, k=1)[0]
        return selected_route

    def route_request_to_worker(self):
        selected_route = self.select_worker_route()