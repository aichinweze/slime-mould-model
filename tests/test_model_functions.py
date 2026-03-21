import unittest
import numpy as np

from slime_mould.model_functions import *

class ModelFunctionsTestCases(unittest.TestCase):
    def setUp(self):
        self.number_of_nodes = 5
        self.source_nodes = [0, 1]
        self.sink_nodes = [4]
        self.connection_dict_five_nodes = {
            0: [1, 3],
            1: [0, 2],
            2: [1, 3],
            3: [0, 2, 4],
            4: [3]
        }
        self.epsilon = 0.3
        self.mu = 0.022
        self.alpha = 0.13
        self.d_min = 1e-4
        self.d_max = 1.75

    # Testing build flow vector function
    def test_build_flow_vector_normal(self):
        number_of_nodes = 5
        source_nodes = self.source_nodes
        sink_nodes = self.sink_nodes

        expected_flow_vector = np.array([1/2, 1/2, 0, 0, -1], dtype=float)
        derived_flow_vector = build_flow_vector(number_of_nodes, source_nodes, sink_nodes)
        self.assertTrue(np.all(expected_flow_vector == derived_flow_vector))

    def test_build_flow_vector_zero(self):
        number_of_nodes = 10
        source_nodes = [0, 1, 5]
        sink_nodes = []

        expected_flow_vector = np.zeros(number_of_nodes, dtype=float)
        derived_flow_vector = build_flow_vector(number_of_nodes, source_nodes, sink_nodes)
        self.assertTrue(np.all(expected_flow_vector == derived_flow_vector))

    def test_build_flow_vector_bad_indices(self):
        number_of_nodes = 7
        source_nodes = [0, 7]
        sink_nodes = [2]

        expected_flow_vector = np.zeros(number_of_nodes, dtype=float)
        derived_flow_vector = build_flow_vector(number_of_nodes, source_nodes, sink_nodes)
        self.assertTrue(np.all(expected_flow_vector == derived_flow_vector))


    # Testing build adjacency matrix function
    def test_build_adjacency_matrix(self):
        connection_dict = self.connection_dict_five_nodes

        expected_adjacency_matrix = np.array([
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1],
            [0, 0, 0, 1, 0]
        ])
        derived_adjacency_matrix = build_adjacency_matrix(connection_dict)

        self.assertTrue(np.all(expected_adjacency_matrix == derived_adjacency_matrix))

    def test_build_adjacency_matrix_no_dict(self):
        connection_dict = {}
        self.assertRaises(ValueError, build_adjacency_matrix, connection_dict)


    # Testing update pressure at node function
    def test_update_pressure_at_node(self):
        number_of_nodes = self.number_of_nodes
        source_nodes = self.source_nodes
        sink_nodes = self.sink_nodes
        epsilon = self.epsilon

        pressure_index = 4

        flow_vector = build_flow_vector(number_of_nodes, source_nodes, sink_nodes)
        flow_at_node: float = flow_vector[pressure_index]
        pressure_vector = np.zeros(number_of_nodes, dtype=int)

        connection_dict = self.connection_dict_five_nodes
        adjacency_matrix = build_adjacency_matrix(connection_dict)
        conductivity_at_row = adjacency_matrix[pressure_index]

        expected_pressure = -1
        derived_pressure = update_pressure_at_node(pressure_index, pressure_vector, conductivity_at_row, flow_at_node, epsilon)

        self.assertEqual(expected_pressure, derived_pressure)

    # Testing update conductivity row function
    def test_update_conductivity_at_row(self):
        row_index = 1
        connection_dict = self.connection_dict_five_nodes
        adjacency_matrix = build_adjacency_matrix(connection_dict)
        conductivity_at_row = adjacency_matrix[row_index]
        efficiency_matrix_row = conductivity_at_row

        pressure_vector = np.array([1/2, 1/2, 0, 0, -1])
        expected_conductivity = np.array([0.978, 0, (0.978 + ((3*self.alpha)/14)), 0, 0])
        derived_conductivity = update_conductivity_row(
            row_index,
            conductivity_at_row,
            efficiency_matrix_row,
            pressure_vector,
            self.mu,
            self.alpha,
            self.d_max,
            self.d_min
        )

        self.assertTrue(np.all(expected_conductivity == derived_conductivity))


if __name__ == '__main__':
    unittest.main()
