import logging

import numpy as np
from numpy.typing import NDArray

from models.models import RouteWeight, Metrics


def get_route_conductivities_from_route_weight(source_route_weights: list[RouteWeight]) -> dict[str, float]:
    source_entries: dict[str, float] = {}

    if len(source_route_weights) == 0:
        raise ValueError("Source route weights must have at least one route weight")
    else:
        for route_weight in source_route_weights:
            edge_id = route_weight.get_edge_id()
            conductivity = route_weight.get_conductivity()
            source_entries[edge_id] = conductivity
    return source_entries


def get_source_metrics_dict(source_metrics: list[Metrics], gamma: float = 1e-3) -> dict[str, float]:
    source_entries = {}

    if len(source_metrics) == 0:
        raise ValueError("There must be metrics present for the source node.")
    else:
        latencies = [metric.get_avg_latency() for metric in source_metrics]
        min_latency = min(latencies)

        for metric in source_metrics:
            source_entries[metric.get_edge_id()] = min_latency / (metric.get_avg_latency() + gamma)

    return source_entries

def get_worker_node_entries(
        source_conductivities: dict[str, float],
        edge_delimiter: str = ">>",
        sink_node: int = 4
) -> dict[str, float]:
    worker_conductivities = {}

    for key, value in source_conductivities.items():
        nodes = key.split(edge_delimiter)
        reversed_edge = f'{nodes[1]}{edge_delimiter}{nodes[0]}'
        to_sink_edge = f'{nodes[1]}{edge_delimiter}{sink_node}'
        worker_conductivities[reversed_edge] = value
        worker_conductivities[to_sink_edge] = value

    return worker_conductivities

def get_sink_node_entries(
        source_conductivities: dict[str, float],
        edge_delimiter: str = ">>",
        sink_node: int = 4
) -> dict[str, float]:
    sink_conductivities = {}

    for key, value in source_conductivities.items():
        nodes = key.split(edge_delimiter)
        from_sink_edge = f'{sink_node}{edge_delimiter}{nodes[1]}'
        sink_conductivities[from_sink_edge] = value

    return sink_conductivities


def build_matrix_from_source_conductivities(
        source_conductivities: dict[str, float],
        number_of_edges_from_source: int = 3,
        edge_delimiter: str = ">>",
        number_of_nodes: int = 5
) -> NDArray[float]:
    zeros_matrix = np.zeros((number_of_nodes, number_of_nodes))
    updated_matrix = zeros_matrix

    worker_conductivities = get_worker_node_entries(source_conductivities, edge_delimiter=edge_delimiter)
    sink_conductivities = get_sink_node_entries(source_conductivities, edge_delimiter=edge_delimiter)
    complete_conductivities = source_conductivities | worker_conductivities | sink_conductivities

    if len(source_conductivities) != number_of_edges_from_source:
        logging.warn("Fewer rows retrieved than expecting. Creating zeros matrix of appropriate dimensions...")
        return zeros_matrix
    else:
        for key, value in complete_conductivities.items():
            nodes = key.split(edge_delimiter)
            row, col = int(nodes[0]), int(nodes[1])
            updated_matrix[row, col] = value

        return updated_matrix

def get_edge_ids_from_dict(
        edges_dict: dict[int, list[int]],
        edge_delimiter: str = ">>",
        source_node: int = 0
) -> list[str]:
    source_edges = edges_dict.get(source_node, [])

    edge_ids = []
    for edge in source_edges:
        edge_id = f'{source_node}{edge_delimiter}{edge}'
        edge_ids.append(edge_id)

    return edge_ids
