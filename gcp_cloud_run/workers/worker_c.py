import time
import requests

from ..models.models import CryptoResult
from .worker_base import WorkerBase

class WorkerC(WorkerBase):
    def __init__(self, node_id: int, source_currency: str, target_currency: str, start_timestamp: str, delay: int = 15):
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
        response_json = response.json()
        crypto_result = self.extract_crypto_result(response_json)

        time.sleep(self.delay)
        self.set_end_timestamp()
        self.add_latency_to_result()

        crypto_result_dict = crypto_result.to_dict()
        crypto_result_dict["execution_time"] = self.execution_time

        print("Worker C: execute: completed job --> {}".format(crypto_result_dict))

        return crypto_result_dict


