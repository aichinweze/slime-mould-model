import time
import requests

from ..models.models import CryptoResult
from .worker_base import WorkerBase

class WorkerA(WorkerBase):
    def __init__(self, node_id: int, source_currency: str, target_currency: str, delay: int = 1):
        super().__init__(
            node_id=node_id,
            source_currency=source_currency,
            target_currency=target_currency
        )
        self.delay = delay

    def execute(self) -> CryptoResult:
        request_url = self.build_crypto_price_url(self.currency_pair)

        response = requests.get(request_url)
        response_json = response.json()
        crypto_result = self.extract_crypto_result(response_json)

        time.sleep(self.delay)

        print("Worker A: execute: completed job --> {}".format(crypto_result.to_dict()))

        return crypto_result
