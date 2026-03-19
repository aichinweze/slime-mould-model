import logging
import time

import requests

from workers.worker_base import WorkerBase


class WorkerA(WorkerBase):
    def __init__(self, node_id: int, source_currency: str, target_currency: str, start_timestamp: str, delay: int = 1):
        super().__init__(
            node_id=node_id,
            source_currency=source_currency,
            target_currency=target_currency,
            start_timestamp=start_timestamp
        )
        self.delay = delay

    def execute(self) -> dict:
        request_url = self.build_crypto_price_url(self.currency_pair)

        response = requests.get(request_url)
        self.set_end_timestamp()
        self.add_latency_to_result()

        response_json = response.json()

        crypto_result = self.extract_crypto_result(response_json)
        crypto_result_dict = crypto_result.to_dict()
        crypto_result_dict["execution_time"] = self.execution_time

        time.sleep(self.delay)

        logging.debug("Worker A: execute: completed job --> {}".format(crypto_result_dict))

        return crypto_result_dict
