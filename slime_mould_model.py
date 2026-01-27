import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def update_conductivity(edges_matrix, conductivity_matrix, start, end, r=1, inverse_length=None):
    if inverse_length is None:
        # TODO: Will need to be updated when lengths are variable
        inverse_length = np.where(edges_matrix == 0, 0, 1 / edges_matrix)

    conductivity_by_length = conductivity_matrix * inverse_length

    reverse_conductivity = np.where(conductivity_by_length != 0, -conductivity_by_length, conductivity_by_length)

    row_sums = np.sum(reverse_conductivity, axis=1) * -1

    diagonal_indices = np.diag_indices_from(reverse_conductivity)

    reverse_conductivity[diagonal_indices] = row_sums

    pressure_sink_node = end

    flow_vector = np.zeros(number_of_nodes)
    flow_vector[start] = -1
    flow_vector[end] = 1

    reduced_flow_vector = np.delete(flow_vector, pressure_sink_node, axis=0)

    reduced_conductivity_removed_row = np.delete(reverse_conductivity, pressure_sink_node, axis=0)
    reduced_conductivity = np.delete(reduced_conductivity_removed_row, pressure_sink_node, axis=1)

    inverse_conductivity = np.linalg.inv(reduced_conductivity)
    pressure_vector = np.matmul(inverse_conductivity, reduced_flow_vector)

    complete_pressure_vector = np.insert(pressure_vector, pressure_sink_node, 0)

    flux = np.zeros_like(conductivity_by_length)

    for idx, element in np.ndenumerate(conductivity_by_length):
        if element != 0:
            (row, col) = idx
            flux[idx] = abs(element * (complete_pressure_vector[row] - complete_pressure_vector[col]))

    derivative = flux - r * conductivity_matrix

    return conductivity_matrix + derivative


edges = np.array(
        [[0, 1, 0, 0],
         [1, 0, 1, 1],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
)

start_node = 0
end_node = 2

number_of_nodes = edges.shape[0]
initialiser_rows = number_of_nodes
initialiser_cols = number_of_nodes

initialiser = np.array([[1 for _ in range(initialiser_cols)] for _ in range(initialiser_rows)])

initial_conductivity = edges * initialiser

G = nx.Graph(edges)
pos = nx.spring_layout(G, seed=2797)

last_conductivity = initial_conductivity
for i in range(3):
    edge_weights = [float(last_conductivity[u][v]) * 10 for u, v in G.edges()]
    nx.draw_networkx_nodes(G, pos, node_color='black', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='red', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_color='green', node_size=500)
    nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color='gray', alpha=0.3)

    plt.show()
    updated_conductivity = update_conductivity(edges, last_conductivity, start_node, end_node)

    if np.array_equal(last_conductivity, updated_conductivity):
        break
    else:
        last_conductivity = updated_conductivity



