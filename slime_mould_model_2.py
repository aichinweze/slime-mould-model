import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from numpy.ma.core import outer

from numpy.typing import NDArray

def make_adjacency_matrix(connection_dict: dict[int, list[int]]):
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
    flow_at_node: int,
    epsilon: float
):
    neighbour_avg_numer = sum([(val * pressure_vector[idx]) for (idx, val) in enumerate(conductivity_by_l_row)])
    neighbour_avg_denom = np.sum(conductivity_by_l_row)
    neighbour_avg = neighbour_avg_numer / neighbour_avg_denom

    pressure_at_node = pressure_vector[pressure_index]

    return ((1 - epsilon) * pressure_at_node) + (epsilon * neighbour_avg) + flow_at_node


def update_conductivity_row(
    row_index: int,
    conductivity_row: NDArray[float],
    conductivity_by_length_row: NDArray[float],
    pressure_vector: NDArray[float],
    mu: float,
    r: float,
    d_max: float = 1.0,
):
    adjusted_conductivity = (1 - mu) * conductivity_row
    flow_change = [
        (abs(r * val * (pressure_vector[row_index] - pressure_vector[idx])) * (1 - (conductivity_row[idx]/d_max)))
        for (idx, val) in enumerate(conductivity_by_length_row)
    ]

    return adjusted_conductivity + flow_change


edges_dict = {
    0: [1],
    1: [0, 2, 3],
    2: [1],
    3: [1]
}

edges_dict_2 = {
    0: [1],
    1: [0, 2, 4],
    2: [1, 3, 5],
    3: [2],
    4: [1, 5],
    5: [2, 4]
}

edges_dict_3 = {
    0: [3],
    1: [5],
    2: [3, 7],
    3: [0, 2, 8],
    4: [5, 9],
    5: [4, 6],
    6: [5, 11],
    7: [2, 8],
    8: [3, 7, 9, 12],
    9: [4, 8, 10, 13],
    10: [9, 11, 14],
    11: [8, 10],
    12: [8],
    13: [9, 14],
    14: [10, 13, 15],
    15: [14]
}


# edges = make_adjacency_matrix(edges_dict)
edges = make_adjacency_matrix(edges_dict_2)
adj_matrix = np.array(edges, dtype=int)
print(adj_matrix)

start_node = 0
end_node = 3

r = 0.01
mu = 0.025
epsilon = 0.2

number_of_nodes = adj_matrix.shape[0]
initialiser_rows = number_of_nodes
initialiser_cols = number_of_nodes
initialiser = np.array([[1 for _ in range(initialiser_cols)] for _ in range(initialiser_rows)])
inverse_length = np.where(adj_matrix == 0, 0, 1 / adj_matrix)

initial_conductivity = adj_matrix * initialiser
initial_pressure: NDArray[int] = np.zeros(number_of_nodes, dtype=int)

flow_vector: NDArray[int] = np.zeros(number_of_nodes, dtype=int)
indices_to_update = [start_node, end_node]
values_to_update = [1, -1]
flow_vector[indices_to_update] = values_to_update

G = nx.Graph(adj_matrix)
pos = nx.spring_layout(G, seed=27)

last_conductivity = initial_conductivity
last_pressure = initial_pressure

print("Flow vector")
print(flow_vector)
print("Initial pressure")
print(initial_pressure)
print("Initial conductivity")
print(initial_conductivity)
print("Initial conductivity by length")
print(initial_conductivity * inverse_length)

stable_point = False

pressure_loop = 25
outer_loop_length = 350

plt.ion()

# while not stable_point:
for n in range(outer_loop_length):
    edge_weights = [float(last_conductivity[u][v]) * 10 for u, v in G.edges()]
    nx.draw_networkx_nodes(G, pos, node_color='black', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='red', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_color='green', node_size=500)
    nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color='gray', alpha=0.3)

    plt.pause(0.01)

    conductivity_by_length = last_conductivity * inverse_length

    for nn in range(pressure_loop):
        next_pressure = np.array([update_pressure_at_node(i, last_pressure, last_conductivity[i], flow_vector[i], epsilon) for i in range(last_pressure.size)])
        last_pressure = next_pressure
        # print("Next pressure")
        # print(str(next_pressure))

    updated_conductivity = [update_conductivity_row(i, last_conductivity[i], conductivity_by_length[i], last_pressure, mu, r) for i in range(number_of_nodes)]

    # print("Next conductivity")
    # print(str(updated_conductivity))

    last_conductivity = updated_conductivity

    if n < outer_loop_length - 1:
        plt.cla()
    else:
        print("Loop complete")

plt.ioff()
plt.show()
plt.close()


