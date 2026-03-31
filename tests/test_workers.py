import unittest
from datetime import datetime

from models.models import time_format, CryptoResult
from workers.worker_a import WorkerA
from workers.worker_b import WorkerB
from workers.worker_c import WorkerC


class WorkerTestCases(unittest.TestCase):
    def setUp(self):
        self.source_currency = 'BTC'
        self.target_currency = 'USD'
        self.timestamp = "2026-03-31 19:00:00.123"

    # Test worker base functions and models
    def test_worker_build_url(self):
        node_id = 1
        worker = WorkerA(node_id, self.source_currency, self.target_currency, self.timestamp)
        expected_url = "https://api.coinbase.com/v2/prices/BTC-USD/spot/"
        derived_url = worker.build_crypto_price_url(worker.currency_pair)
        self.assertEqual(derived_url, expected_url)

    def test_worker_build_edge_ids(self):
        node_id = 2
        worker = WorkerB(node_id, self.source_currency, self.target_currency, self.timestamp)
        expected_edge_id = "0>>2"
        derived_edge_id = worker.build_edge_id()
        self.assertEqual(derived_edge_id, expected_edge_id)

    # Test extracting crypto result from response
    def test_worker_good_response(self):
        node_id = 3
        worker = WorkerC(node_id, self.source_currency, self.target_currency, self.timestamp)
        response = { "data": { "amount": 65902.31 }}

        expected_result = CryptoResult(
            edge_id="0>>3",
            source_currency="BTC",
            target_currency="USD",
            currency_pair="BTC-USD",
            success_response=True,
            timestamp="2026-03-31 19:00:00.123",
            amount=65902.31
        )
        derived_result = worker.extract_crypto_result(response)

        self.assertEqual(derived_result, expected_result)

    def test_worker_error_response(self):
        node_id = 2
        worker = WorkerB(node_id, self.source_currency, self.target_currency, self.timestamp)
        response = { "error": "Error in request to server" }

        expected_result = CryptoResult(
            edge_id="0>>2",
            source_currency="BTC",
            target_currency="USD",
            currency_pair="BTC-USD",
            success_response=False,
            timestamp="2026-03-31 19:00:00.123",
            amount=None,
            error="Error in request to server"
        )
        derived_result = worker.extract_crypto_result(response)

        self.assertEqual(derived_result, expected_result)

    def test_worker_no_response(self):
        node_id = 1
        worker = WorkerA(node_id, self.source_currency, self.target_currency, self.timestamp)
        response = {}

        expected_result = CryptoResult(
                edge_id="0>>1",
                source_currency="BTC",
                target_currency="USD",
                currency_pair="BTC-USD",
                success_response=False,
                timestamp="2026-03-31 19:00:00.123",
                amount=None,
                error="Other error in curl request"
            )
        derived_result = worker.extract_crypto_result(response)

        self.assertEqual(derived_result, expected_result)


if __name__ == '__main__':
    unittest.main()
