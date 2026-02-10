import numpy as np
from numpy.typing import NDArray


def build_flow_vector(number_of_nodes: int, source_nodes: list[int], sink_nodes: list[int]) -> NDArray[float]:
    """
    Build a vector representing the flow between nodes between source and sink nodes. List of source and sink nodes are
    provided as parameters to the function
    """
    positive_flow = len(source_nodes)
    negative_flow = -len(sink_nodes)

    flow_vector = np.zeros(number_of_nodes, dtype=float)
    flow_vector[source_nodes] = 1 / positive_flow
    flow_vector[sink_nodes] = 1 / negative_flow

    return flow_vector

def build_adjacency_matrix(connection_dict: dict[int, list[int]]):
    """Build an adjacency matrix from a dictionary which represents the edges in the matrix."""
    adjacency_matrix = []
    number_of_nodes = len(connection_dict)

    for idx in range(number_of_nodes):
        non_zero_row_indices = connection_dict[idx]
        row = [(1 if arr_index in non_zero_row_indices else 0) for arr_index in range(number_of_nodes)]
        adjacency_matrix.append(row)
    return adjacency_matrix


def update_pressure_at_node(
    pressure_index: int,
    pressure_vector: NDArray[float],
    conductivity_by_l_row: NDArray[float],
    flow_at_node: float,
    epsilon: float
) -> NDArray[float]:
    """Update pressure for a given node in the graph."""
    neighbour_avg_numer = sum([(val * pressure_vector[idx]) for (idx, val) in enumerate(conductivity_by_l_row)])
    neighbour_avg_denom = np.sum(conductivity_by_l_row)
    neighbour_avg = neighbour_avg_numer / neighbour_avg_denom

    pressure_at_node = pressure_vector[pressure_index]

    return ((1 - epsilon) * pressure_at_node) + (epsilon * neighbour_avg) + flow_at_node


def update_pressure(
    conductivity_by_l_matrix: NDArray[float],
    flow_vector: NDArray[float],
    epsilon: float
) -> NDArray[float]:
    """
    Update pressure for all nodes in the graph. Pressure is updated by taking a weighted average of pressure from
    neighbouring nodes. Weight is provided by conductivity.
    """
    number_of_nodes: int = conductivity_by_l_matrix.shape[0]
    pressure_vector: NDArray[float] = np.zeros(number_of_nodes)

    return np.array(
        [
            update_pressure_at_node(
                i,
                pressure_vector,
                conductivity_by_l_matrix[i],
                flow_vector[i],
                epsilon
            ) for i in range(number_of_nodes)
        ]
    )


def update_conductivity_row(
    row_index: int,
    conductivity_row: NDArray[float],
    conductivity_by_length_row: NDArray[float],
    pressure_vector: NDArray[float],
    mu: float,
    r: float,
    d_max: float,
    d_min: float
) -> NDArray[float]:
    """Update conductivity for the edges connected to a given node on the graph."""
    adjusted_conductivity = (1 - mu) * conductivity_row

    flow_change = [
        (abs(r * val * (pressure_vector[row_index] - pressure_vector[idx])) * (1 - (conductivity_row[idx]/d_max)))
        for (idx, val) in enumerate(conductivity_by_length_row)
    ]

    updated_conductivity = adjusted_conductivity + flow_change

    return np.where(updated_conductivity > d_min, updated_conductivity, 0)


def update_conductivity(
    conductivity_matrix: NDArray[float],
    length_matrix: NDArray[float],
    pressure_vector: NDArray[float],
    mu: float,
    r: float,
    d_max: float,
    d_min: float
) -> NDArray[float]:
    """Update conductivity for all edges in the graph."""
    number_of_nodes: int = conductivity_matrix.shape[0]

    return np.array(
        [update_conductivity_row(
                i,
                conductivity_matrix[i],
                conductivity_matrix[i] / length_matrix[i],
                pressure_vector,
                mu,
                r,
                d_max,
                d_min
            ) for i in range(number_of_nodes)
        ])