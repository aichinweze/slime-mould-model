import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from numpy.typing import NDArray

def make_adjacency_matrix(connection_dict: dict[int, list[int]], number_of_nodes: int):
    adjacency_matrix = []
    for idx in range(len(connection_dict)):
        non_zero_row_indices = connection_dict[idx]
        row = [(1 if arr_index in non_zero_row_indices else 0) for arr_index in range(number_of_nodes)]
        adjacency_matrix.append(row)
    return adjacency_matrix



def combine_pressure_vectors(pressure_sinks, reduced_pressure_vector):
    combined_pressure_vector = reduced_pressure_vector
    for i in sorted(pressure_sinks):
        if i == combined_pressure_vector.size:
            combined_pressure_vector = np.append(combined_pressure_vector, 0)
        else:
            combined_pressure_vector = np.insert(combined_pressure_vector, i, 0)

    return combined_pressure_vector


def get_conductivity_derivative(
        edges_matrix: NDArray[int],
        conductivity_matrix: NDArray[float],
        start: int,
        end: int,
        pressure_sinks: list[int],
        r: int=1,
        inverse_length: NDArray[float]=None
):
    if inverse_length is None:
        # TODO: Will need to be updated when lengths are variable
        inverse_length = np.where(edges_matrix == 0, 0, 1 / edges_matrix)

    conductivity_by_length = conductivity_matrix * inverse_length

    reverse_conductivity = np.where(conductivity_by_length != 0, -conductivity_by_length, conductivity_by_length)

    row_sums: NDArray[float] = np.sum(reverse_conductivity, axis=1) * -1

    diagonal_indices = np.diag_indices_from(reverse_conductivity)

    reverse_conductivity[diagonal_indices] = row_sums

    node_count = edges_matrix.shape[0]
    flow_vector = np.zeros(node_count)
    flow_vector[start] = -1
    flow_vector[end] = 1

    print("Pressure sinks: " + str(pressure_sinks))

    reduced_flow_vector = np.delete(flow_vector, pressure_sinks, axis=0)
    print("Flow vector: ", str(flow_vector))
    print("Reduced Flow vector: ", str(reduced_flow_vector))

    reduced_conductivity_removed_row = np.delete(reverse_conductivity, pressure_sinks, axis=0)
    reduced_conductivity = np.delete(reduced_conductivity_removed_row, pressure_sinks, axis=1)

    inverse_conductivity = np.linalg.inv(reduced_conductivity)
    pressure_vector = np.matmul(inverse_conductivity, reduced_flow_vector)
    print("Pressure vector: ", str(pressure_vector))
    print("Pressure sinks: " + str(sorted(pressure_sinks)))

    complete_pressure_vector = combine_pressure_vectors(pressure_sinks, pressure_vector)
    n_pressure_sinks = { int(idx) for idx in np.where(complete_pressure_vector == 0)[0] }

    complete_pressure_sinks = set(pressure_sinks) | n_pressure_sinks

    flux = np.zeros_like(conductivity_by_length)

    for idx, element in np.ndenumerate(conductivity_by_length):
        if element != 0:
            (row, col) = idx
            flux[idx] = abs(element * (complete_pressure_vector[row] - complete_pressure_vector[col]))

    return flux - r * conductivity_matrix, complete_pressure_sinks


# edges = np.array(
#         [[0, 1, 0, 0],
#          [1, 0, 1, 1],
#          [0, 1, 0, 0],
#          [0, 1, 0, 0]]
# )

# edges = np.array(
#         [[0, 1, 0, 0, 0, 0, 0],
#          [1, 0, 1, 0, 1, 0, 0],
#          [0, 1, 0, 1, 0, 0, 0],
#          [0, 0, 1, 0, 0, 0, 0],
#          [0, 1, 0, 0, 0, 1, 1],
#          [0, 0, 0, 0, 1, 0, 0],
#          [0, 0, 0, 0, 1, 0, 0]]
# )

# edges = np.array([
#         [0, 1, 0, 0, 0, 0, 0],
#         [1, 0, 1, 0, 1, 0, 0],
#         [0, 1, 0, 1, 0, 1, 0],
#         [0, 0, 1, 0, 0, 0, 0],
#         [0, 1, 0, 0, 0, 1, 1],
#         [0, 0, 1, 0, 1, 0, 0],
#         [0, 0, 0, 0, 1, 0, 0]
#     ],
#     dtype=int
# )

edges_dict = {
    0: [2],
    1: [2, 6],
    2: [0, 1, 3, 7],
    3: [2, 8],
    4: [5, 9],
    5: [4],
    6: [1],
    7: [2, 8, 11],
    8: [3, 7, 9, 12],
    9: [4, 8, 10],
    10: [9],
    11: [7, 12],
    12: [8, 11]
}

edges = make_adjacency_matrix(edges_dict, 13)
adj_matrix = np.array(edges, dtype=int)
print(adj_matrix)

start_node = 0
end_node = 5

number_of_nodes = adj_matrix.shape[0]
initialiser_rows = number_of_nodes
initialiser_cols = number_of_nodes
initialiser = np.array([[1 for _ in range(initialiser_cols)] for _ in range(initialiser_rows)])

initial_conductivity = adj_matrix * initialiser

G = nx.Graph(adj_matrix)
pos = nx.spring_layout(G, seed=2797)

last_conductivity = initial_conductivity
last_pressure_sinks: list[int] = [end_node]

stable_point = False
i = 0

while not stable_point:
    print("Iteration " + str(i))
    edge_weights = [float(last_conductivity[u][v]) * 10 for u, v in G.edges()]
    nx.draw_networkx_nodes(G, pos, node_color='black', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='red', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_color='green', node_size=500)
    nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color='gray', alpha=0.3)

    plt.show()

    conductivity_derivative, updated_pressure_sinks = get_conductivity_derivative(adj_matrix, last_conductivity, start_node, end_node, last_pressure_sinks)

    if (conductivity_derivative == 0).all():
        print("Escaping iteration at " + str(i))
        stable_point = True
        break
    else:
        updated_conductivity = last_conductivity + conductivity_derivative

        conductivity_row_sums = np.sum(updated_conductivity, axis=1)
        new_pressure_sinks = np.where(conductivity_row_sums == 0)
        new_pressure_sink_indices = [int(i) for i in new_pressure_sinks[0]]

        next_pressure_sinks = sorted(updated_pressure_sinks | set(new_pressure_sink_indices), reverse=True)

        print("Last pressure sinks: " + str(last_pressure_sinks))
        print("Updated pressure sinks: " + str(next_pressure_sinks))
        print("Last conductivity: \n" + str(last_conductivity))
        print("Updated conductivity: \n" + str(updated_conductivity))

        last_conductivity = updated_conductivity
        last_pressure_sinks = next_pressure_sinks
        i += 1



