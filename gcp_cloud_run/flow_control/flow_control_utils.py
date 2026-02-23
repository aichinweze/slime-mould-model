import numpy as np
from numpy.typing import NDArray

from ..models.models import RouteWeight, Metrics


def get_source_entries_from_route_weight(source_route_weights: list[RouteWeight]) -> dict[str, float]:
    source_entries: dict[str, float] = {}

    for route_weight in source_route_weights:
        edge_id = route_weight.get_edge_id()
        conductivity = route_weight.get_conductivity()
        source_entries[edge_id] = conductivity

    return source_entries


def get_source_entries_from_metrics(source_metrics: list[Metrics], gamma: float = 1e-3) -> dict[str, float]:
    source_entries = {}
    latencies = [metric.avg_latency for metric in source_metrics]
    min_latency = min(latencies)

    for metric in source_metrics:
        source_entries[metric.edge_id] = min_latency / (metric.avg_latency + gamma)

    return source_entries

def get_worker_node_entries(
        source_entries: dict[str, float],
        edge_delimiter: str = ">>",
        sink_node: int = 4
) -> dict[str, float]:
    worker_conductivities = {}

    for key, value in source_entries.items():
        nodes = key.split(edge_delimiter)
        reversed_edge = f'{nodes[1]}{edge_delimiter}{nodes[0]}'
        to_sink_edge = f'{nodes[1]}{edge_delimiter}{sink_node}'
        worker_conductivities[reversed_edge] = value
        worker_conductivities[to_sink_edge] = value

    return worker_conductivities

def get_sink_node_entries(
        source_entries: dict[str, float],
        edge_delimiter: str = ">>",
        sink_node: int = 4
) -> dict[str, float]:
    sink_conductivities = {}

    for key, value in source_entries.items():
        nodes = key.split(edge_delimiter)
        from_sink_edge = f'{sink_node}{edge_delimiter}{nodes[1]}'
        sink_conductivities[from_sink_edge] = value

    return sink_conductivities


def build_matrix_from_edge_weights(
        source_entries: dict[str, float],
        number_of_edges: int = 3,
        edge_delimiter: str = ">>",
        number_of_nodes: int = 5
) -> NDArray[float]:
    zeros_matrix = np.zeros((number_of_nodes, number_of_nodes))
    updated_matrix = zeros_matrix

    worker_conductivities = get_worker_node_entries(source_entries, edge_delimiter=edge_delimiter)
    sink_conductivities = get_sink_node_entries(source_entries, edge_delimiter=edge_delimiter)

    complete_conductivities = source_entries | worker_conductivities | sink_conductivities

    if len(source_entries) != number_of_edges:
        # TODO: Do something - fewer rows were retrieved than expected
        return zeros_matrix
    else:
        for key, value in complete_conductivities.items():
            nodes = key.split(edge_delimiter)
            row, col = int(nodes[0]), int(nodes[1])
            updated_matrix[row, col] = value

        return updated_matrix


# TODO: Move to unit test
# rw_1 = RouteWeight(edge_id="0>>1", conductivity=0.5, timestamp="fake-time", iteration=0)
# rw_2 = RouteWeight(edge_id="0>>2", conductivity=0.1, timestamp="fake-time", iteration=0)
# rw_3 = RouteWeight(edge_id="0>>3", conductivity=0.6, timestamp="fake-time", iteration=0)
#
# source_cond = get_source_entries_from_route_weight([rw_1, rw_2, rw_3])
# cond_matrix = build_matrix_from_edge_weights(source_cond)
#
# print(source_cond)
# print(cond_matrix)
#
# m_1 = Metrics(edge_id="0>>1", avg_latency=1.6, timestamp="fake-time")
# m_2 = Metrics(edge_id="0>>2", avg_latency=17, timestamp="fake-time")
# m_3 = Metrics(edge_id="0>>3", avg_latency=12, timestamp="fake-time")
#
# source_metrics = get_source_entries_from_metrics([m_1, m_2, m_3])
# eff_matrix = build_matrix_from_edge_weights(source_metrics)
#
# print(source_metrics)
# print(eff_matrix)