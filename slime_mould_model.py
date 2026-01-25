from logging import getLevelNamesMapping

import numpy as np

edges = np.array(
        [[0, 1, 0, 0],
         [1, 0, 1, 1],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
)

# TODO: Will need to be updated when lengths are variable
inverse_length = np.where(edges == 0, 0, 1/edges)

number_of_nodes = 4
initialiser_rows = number_of_nodes
initialiser_cols = number_of_nodes

initialiser = np.array([[1 for _ in range(initialiser_cols)] for _ in range(initialiser_rows)])

conductivity = edges * initialiser
print(conductivity)

conductivity_by_length = conductivity * inverse_length

reverse_conductivity = np.where(conductivity_by_length != 0, -conductivity_by_length, conductivity_by_length)

row_sums = np.sum(reverse_conductivity, axis=1) * -1

diagonal_indices = np.diag_indices_from(reverse_conductivity)

reverse_conductivity[diagonal_indices] = row_sums

# print(reverse_conductivity)

start_node = 0
end_node = 2

pressure_sink_node = 2

flow_vector = np.zeros(number_of_nodes)
flow_vector[start_node] = -1
flow_vector[end_node] = 1
# print(flow_vector)

reduced_flow_vector = np.delete(flow_vector, pressure_sink_node, axis=0)
# print(reduced_flow_vector)

reduced_conductivity_removed_row = np.delete(reverse_conductivity, pressure_sink_node, axis=0)
reduced_conductivity = np.delete(reduced_conductivity_removed_row, pressure_sink_node, axis=1)

# print(reduced_conductivity)

inverse_conductivity = np.linalg.inv(reduced_conductivity)
pressure_vector = np.matmul(inverse_conductivity, reduced_flow_vector)

# print(pressure_vector)

complete_pressure_vector = np.insert(pressure_vector, pressure_sink_node, 0)
print(complete_pressure_vector)

flux = np.zeros_like(conductivity_by_length)

for idx, element in np.ndenumerate(conductivity_by_length):
    if element != 0:
        (row, col) = idx
        flux[idx] = abs(element * (complete_pressure_vector[row] - complete_pressure_vector[col]))

print(flux)

r = 1
derivative = flux - r*conductivity
print(derivative)

node_coords = {0: (4, 0), 1: (2, 0), 2: (2, 2), 3: (0, 0)}
tube_coords = {0: (3, 0), 1: (1, 0), 2: (2, 1)}

tube_mapping = {0: (0, 1), 1: (1, 3), 2: (1, 2)}

rows = 5
cols = 3

grid = np.full((rows, cols), "-", dtype=object)

for key, value in node_coords.items():
    grid[value] = "N"

for key, value in tube_coords.items():
    tube_value = str(conductivity[tube_mapping[key]])
    grid[value] = tube_value

print(grid)


updated_conductivity = conductivity + derivative

grid = np.full((rows, cols), "-", dtype=object)

for key, value in node_coords.items():
    grid[value] = "N"

for key, value in tube_coords.items():
    tube_value = str(updated_conductivity[tube_mapping[key]])
    grid[value] = tube_value

print(grid)



# def print_grid(conductivity_matrix, node_coords, tube_coords, tube_mapping):
#     rows = 5
#     cols = 3
#
#     grid = np.full((rows, cols), "X", dtype=object)
#
#     for key, value in node_coords.items():
#         grid[value] = "O"
#


