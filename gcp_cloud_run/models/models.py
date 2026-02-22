from dataclasses import dataclass

@dataclass
class CryptoResult:
    source_currency: str
    target_currency: str
    currency_pair: str
    success_response: bool
    amount: float | None
    error: str | None

@dataclass
class CryptoQueryParams:
    source_currency: str
    target_currency: str

class RouteWeight:
    def __init__(self, edge_id: str, conductivity: float):
        self.edge_id = edge_id
        self.conductivity = conductivity

    def get_conductivity(self) -> float:
        return self.conductivity

    def get_edge_id(self) -> str:
        return self.edge_id

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "conductivity": self.conductivity
        }

    @staticmethod
    def from_dict(source: dict):
        return RouteWeight(
            source["edge_id"],
            source["conductivity"]
        )


class GraphRouteWeights:
    def __init__(self, route_weights: list[RouteWeight], iteration: int, timestamp: str):
        self.route_weights = route_weights
        self.iteration = iteration
        self.timestamp = timestamp

    def get_iteration(self):
        return self.iteration

    def get_route_weights(self) -> list[RouteWeight]:
        return self.route_weights

    def get_timestamp(self) -> str:
        return self.timestamp

    def to_dict(self) -> dict:
        return {
            "route_weights": [route_weight.to_dict() for route_weight in self.route_weights],
            "iteration": self.iteration,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(source: dict):
        return GraphRouteWeights(
            source["route_weights"],
            source["iteration"],
            source["timestamp"]
        )


class Metrics:
    def __init__(self, edge_id: str, avg_latency: float, timestamp: str):
        self.edge_id = edge_id
        self.avg_latency = avg_latency
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "avg_latency": self.avg_latency,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(source: dict):
        return Metrics(
            source["edge_id"],
            source["avg_latency"],
            source["timestamp"]
        )

