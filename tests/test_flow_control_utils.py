import unittest

from utils.flow_control_utils import *


class FlowControlTestCases(unittest.TestCase):
    def setUp(self):
        self.source_conductivities = { "0>>1": 0.5, "0>>2": 0.1, "0>>3": 0.6 }
        self.gamma = 0.5

    def test_get_route_conductivities_from_route_weights(self):
        rw_1 = RouteWeight(edge_id="0>>1", conductivity=0.5)
        rw_2 = RouteWeight(edge_id="0>>2", conductivity=0.1)
        rw_3 = RouteWeight(edge_id="0>>3", conductivity=0.6)

        derived_route_conductivities = get_route_conductivities_from_route_weight([rw_1, rw_2, rw_3])
        self.assertEqual(self.source_conductivities, derived_route_conductivities)

    def test_get_route_conductivities_from_edge_weights_null(self):
        self.assertRaises(ValueError, get_route_conductivities_from_route_weight, [])

    def test_get_source_metrics_dict(self):
        m_1 = Metrics(edge_id="0>>1", avg_latency=1.6, timestamp="fake-time", document_count=1)
        m_2 = Metrics(edge_id="0>>2", avg_latency=17, timestamp="fake-time", document_count=1)
        m_3 = Metrics(edge_id="0>>3", avg_latency=12, timestamp="fake-time", document_count=1)

        expected_source_dict = { "0>>1": 16.0/21, "0>>2": 16.0/175, "0>>3": 16.0/125 }
        derived_source_dict = get_source_metrics_dict([m_1, m_2, m_3], self.gamma)
        self.assertEqual(expected_source_dict, derived_source_dict)

    def test_get_worker_node_entries(self):
        expected_worker_node_entries = {
            "1>>0": 0.5,
            "1>>4": 0.5,
            "2>>0": 0.1,
            "2>>4": 0.1,
            "3>>0": 0.6,
            "3>>4": 0.6
        }
        derived_worker_node_entries = get_worker_node_entries(self.source_conductivities)
        self.assertEqual(expected_worker_node_entries, derived_worker_node_entries)

    def test_get_sink_node_entries(self):
        source_conductivities = {"0>>1": 0.5, "0>>2": 0.1, "0>>3": 0.6}
        expected_sink_node_entries = { "4>>1": 0.5, "4>>2": 0.1, "4>>3": 0.6 }
        derived_sink_node_entries = get_sink_node_entries(source_conductivities)
        self.assertEqual(expected_sink_node_entries, derived_sink_node_entries)

    def test_build_matrix_from_edge_weights(self):
        expected_conductivity_matrix = np.array([
            [0, 0.5, 0.1, 0.6, 0],
            [0.5, 0, 0, 0, 0.5],
            [0.1, 0, 0, 0, 0.1],
            [0.6, 0, 0, 0, 0.6],
            [0, 0.5, 0.1, 0.6, 0]
        ])
        derived_conductivity_matrix = build_matrix_from_source_conductivities(self.source_conductivities)
        self.assertTrue(np.all(expected_conductivity_matrix == derived_conductivity_matrix))

    def test_build_matrix_from_bad_conductivities(self):
        bad_source_conductivities = { "0>>1": 0.5 }
        expected_conductivity_matrix = np.zeros((5, 5))
        derived_conductivity_matrix = build_matrix_from_source_conductivities(bad_source_conductivities)
        self.assertTrue(np.all(expected_conductivity_matrix == derived_conductivity_matrix))


if __name__ == '__main__':
    unittest.main()
