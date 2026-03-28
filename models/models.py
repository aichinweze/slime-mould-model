from dataclasses import dataclass
from datetime import datetime, timezone

time_format = "%Y-%m-%d %H:%M:%S.%f"

@dataclass
class SlimeMouldParams:
    alpha: float
    mu: float
    epsilon: float
    d_max: float
    d_min: float

class CryptoResult:
    def __init__(self,
                 edge_id: str,
                 source_currency: str,
                 target_currency: str,
                 currency_pair: str,
                 success_response: bool,
                 timestamp: str | None = None,
                 execution_time: float | None = None,
                 amount: float | None = None,
                 error: str | None = None
    ):
        self.edge_id = edge_id
        self.source_currency = source_currency
        self.target_currency = target_currency
        self.currency_pair = currency_pair
        self.success_response = success_response
        self.timestamp = timestamp
        self.execution_time = execution_time
        self.amount = amount
        self.error = error

    def get_edge_id(self):
        return self.edge_id

    def get_execution_time(self):
        return self.execution_time

    def set_timestamp(self):
        self.timestamp = datetime.now(timezone.utc).strftime(time_format)

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_currency": self.source_currency,
            "target_currency": self.target_currency,
            "currency_pair": self.currency_pair,
            "success_response": self.success_response,
            "timestamp": {"string": self.timestamp } if self.timestamp is not None else None,
            "execution_time": self.execution_time,
            "amount": self.amount,
            "error": {"string": self.error} if self.error is not None else None
        }

    @staticmethod
    def from_dict(source: dict):
        return CryptoResult(
            edge_id=source["edge_id"],
            source_currency=source["source_currency"],
            target_currency=source["target_currency"],
            currency_pair=source["currency_pair"],
            success_response=source["success_response"],
            timestamp=source["timestamp"],
            execution_time=source["execution_time"],
            amount=source["amount"],
            error=source["error"]
        )

    def set_execution_time(self, execution_time: float):
        self.execution_time = execution_time

    def __eq__(self, other):
        if not isinstance(other, CryptoResult):
            return NotImplemented
        return self.__dict__ == other.__dict__


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
        route_weights = [RouteWeight.from_dict(route_weight) for route_weight in source["route_weights"]]
        return GraphRouteWeights(
            route_weights,
            source["iteration"],
            source["timestamp"]
        )


class Metrics:
    def __init__(self, edge_id: str, avg_latency: float, document_count: int, timestamp: str):
        self.edge_id = edge_id
        self.avg_latency = avg_latency
        self.document_count = document_count
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "avg_latency": self.avg_latency,
            "document_count": self.document_count,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(source: dict):
        return Metrics(
            source["edge_id"],
            source["avg_latency"],
            source["document_count"],
            source["timestamp"]
        )

    def get_avg_latency(self) -> float:
        return self.avg_latency

    def get_edge_id(self):
        return self.edge_id

    def get_document_count(self):
        return self.document_count

    def __eq__(self, other):
        if not isinstance(other, Metrics):
            return NotImplemented
        return self.__dict__ == other.__dict__