import unittest

from models.models import Metrics
from utils.metrics_utils import aggregate_metrics


class MetricsUtilsTestCases(unittest.TestCase):
    def test_aggregate_metrics_full_history(self):
        metric_1 = Metrics(edge_id="0>>1", avg_latency=2.0, document_count=5, timestamp="")
        metric_2 = Metrics(edge_id="0>>1", avg_latency=2.5, document_count=5, timestamp="")
        metric_3 = Metrics(edge_id="0>>1", avg_latency=2.5, document_count=5, timestamp="")
        metric_4 = Metrics(edge_id="0>>1", avg_latency=2.0, document_count=5, timestamp="")
        new_metric = Metrics(edge_id="0>>1", avg_latency=3.0, document_count=1, timestamp="")

        historical_metrics = [metric_1, metric_2, metric_3, metric_4]
        expected_aggregated_metrics = Metrics(edge_id="0>>1", avg_latency=48.0/21, document_count=5, timestamp="")
        derived_aggregated_metrics = aggregate_metrics(historical_metrics, new_metric)
        self.assertEqual(derived_aggregated_metrics, expected_aggregated_metrics)

    def test_aggregate_metrics_partial_history(self):
        metric_1 = Metrics(edge_id="0>>2", avg_latency=8.0, document_count=1, timestamp="")
        metric_2 = Metrics(edge_id="0>>2", avg_latency=6.5, document_count=2, timestamp="")
        metric_3 = Metrics(edge_id="0>>2", avg_latency=7.5, document_count=3, timestamp="")
        new_metric = Metrics(edge_id="0>>2", avg_latency=7.2, document_count=1, timestamp="")

        historical_metrics = [metric_1, metric_2, metric_3]
        expected_aggregated_metrics = Metrics(edge_id="0>>2", avg_latency= 50.7/7, document_count=4, timestamp="")
        derived_aggregated_metrics = aggregate_metrics(historical_metrics, new_metric)
        self.assertEqual(derived_aggregated_metrics, expected_aggregated_metrics)


if __name__ == '__main__':
    unittest.main()
